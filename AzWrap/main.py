import os
import sys
import json
from pathlib import Path
from datetime import timedelta
from typing import Dict, Any, List, Optional, Union

import click
from dotenv import load_dotenv
import azure.search.documents.indexes.models as azsdim

# Import wrapper classes
from .wrapper import (
    Identity,
    Subscription,
    ResourceGroup,
    SearchService,
    AIService,
    SearchIndexerManager,
    DataSourceConnection,
    Indexer,
    Skillset,
    BlobType
)

from .cli_config import CLI_CONFIG

# Global context object to store common objects and settings
class Context:
    def __init__(self):
        self.verbose = False
        self.quiet = False
        self.output_format = "text"
        self.identity = None
        self.subscription = None
        
    def log(self, message, level="info"):
        """Log a message based on verbose/quiet settings."""
        if self.quiet and level != "error":
            return
            
        if level == "debug" and not self.verbose:
            return
            
        if level == "error":
            click.secho(f"ERROR: {message}", fg="red", err=True)
        elif level == "warning":
            click.secho(f"WARNING: {message}", fg="yellow")
        elif level == "success":
            click.secho(message, fg="green")
        elif level == "debug":
            click.secho(f"DEBUG: {message}", fg="cyan")
        else:
            click.echo(message)

    def output(self, data, title=None):
        """Output data in the specified format."""
        if self.output_format == "json":
            click.echo(json.dumps(data, indent=2, default=str))
        elif self.output_format == "table":
            if isinstance(data, list) and data:
                # Try to create a table
                if title:
                    click.secho(title, fg="blue", bold=True)
                    
                # Extract column names from first item
                if isinstance(data[0], dict):
                    headers = list(data[0].keys())
                    rows = [[str(item.get(h, "")) for h in headers] for item in data]
                    
                    # Print the table header
                    header_row = " | ".join(headers)
                    click.echo(header_row)
                    click.echo("-" * len(header_row))
                    
                    # Print table rows
                    for row in rows:
                        click.echo(" | ".join(row))
                else:
                    # Can't create a proper table, fall back to text
                    for item in data:
                        click.echo(str(item))
            else:
                # Output as text for non-list data
                if title:
                    click.secho(title, fg="blue", bold=True)
                click.echo(str(data))
        else:
            # Default to text output
            if title:
                click.secho(title, fg="blue", bold=True)
                
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict):
                        for key, value in item.items():
                            click.echo(f"{key}: {value}")
                        click.echo("---")
                    else:
                        click.echo(str(item))
            elif isinstance(data, dict):
                for key, value in data.items():
                    click.echo(f"{key}: {value}")
            else:
                click.echo(str(data))

pass_context = click.make_pass_decorator(Context, ensure=True)

def load_environment():
    """Load environment variables from .env file."""
    load_dotenv()
    
    # Check if required Azure credentials are available
    tenant_id = os.getenv("AZURE_TENANT_ID")
    client_id = os.getenv("AZURE_CLIENT_ID")
    client_secret = os.getenv("AZURE_CLIENT_SECRET")
    
    missing = []
    if not tenant_id:
        missing.append("AZURE_TENANT_ID")
    if not client_id:
        missing.append("AZURE_CLIENT_ID")
    if not client_secret:
        missing.append("AZURE_CLIENT_SECRET")
        
    if missing:
        click.secho(f"Error: Missing required environment variables: {', '.join(missing)}", fg="red", err=True)
        click.echo("Please set these variables in your .env file or environment.")
        return None
        
    return {
        "tenant_id": tenant_id,
        "client_id": client_id,
        "client_secret": client_secret,
        "subscription_id": os.getenv("AZURE_SUBSCRIPTION_ID")
    }

def process_json_arg(json_arg: str) -> Dict:
    """
    Process a JSON argument which could be a string or a file path.
    
    Args:
        json_arg: JSON string or path to JSON file
        
    Returns:
        Parsed JSON object
    """
    if os.path.isfile(json_arg):
        with open(json_arg, 'r') as f:
            return json.load(f)
    else:
        try:
            return json.loads(json_arg)
        except json.JSONDecodeError:
            raise click.BadParameter(f"Invalid JSON format: {json_arg}")

def create_cli():
    """Create the CLI structure from configuration."""
    
    # Create the main CLI group
    @click.group(name=CLI_CONFIG["name"])
    @click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
    @click.option("--quiet", "-q", is_flag=True, help="Suppress all output except errors and results")
    @click.option("--output", "-o", type=click.Choice(["text", "json", "table"]), default="text",
                  help="Output format (text, json, table)")
    @click.option("--config", type=click.Path(exists=True), help="Path to configuration file")
    @click.pass_context
    def cli(ctx, verbose, quiet, output, config):
        """Azure Wrapper (AzWrap) CLI tool for managing Azure resources."""
        # Initialize the context object
        ctx.obj = Context()
        ctx.obj.verbose = verbose
        ctx.obj.quiet = quiet
        ctx.obj.output_format = output
        
        # Load environment variables
        ctx.obj.log("Loading environment variables", level="debug")
        env = load_environment()
        if not env:
            ctx.obj.log("Failed to load environment variables", level="error")
            sys.exit(1)
            
        # Create identity object
        try:
            ctx.obj.log("Creating identity object", level="debug")
            ctx.obj.identity = Identity(env["tenant_id"], env["client_id"], env["client_secret"])
            
            # If subscription ID is available, initialize subscription
            if env["subscription_id"]:
                ctx.obj.log(f"Initializing subscription with ID: {env['subscription_id']}", level="debug")
                ctx.obj.subscription = ctx.obj.identity.get_subscription(env["subscription_id"])
                
        except Exception as e:
            logger.error(f"Error initializing Azure credentials: {str(e)}")
            click.secho(f"Error initializing Azure credentials: {str(e)}", fg="red", err=True)
            sys.exit(1)
            
        ctx.obj.log("Azure Wrapper CLI initialized", level="debug")
    
    # Add command groups based on the configuration
    for group_name, group_config in CLI_CONFIG["commands"].items():
        group = click.Group(name=group_name, help=group_config["description"])
        cli.add_command(group)
        
        # Add subcommands to the group
        for cmd_name, cmd_config in group_config["subcommands"].items():
            # Create command function
            command_func = create_command_function(group_name, cmd_name, cmd_config)
            
            # Add options to the command
            for option in cmd_config["options"]:
                # Process option attributes
                params = {
                    "help": option.get("help", ""),
                    "required": option.get("required", False),
                    "default": option.get("default", None),
                    "type": click.STRING,  # Default to string type for all params
                }
                
                # Handle flag options
                if option.get("is_flag", False):
                    params["is_flag"] = True
                    params.pop("type")  # Remove type for flag options
                
                # Create the option
                option_name = f"--{option['name']}"
                short_opt = option.get("short")
                if short_opt:
                    # Use the correct format for Click options with short flag
                    command_func = click.option(f"-{short_opt}", option_name, **params)(command_func)
                    continue
                    
                command_func = click.option(option_name, **params)(command_func)
            
            # Add the command to the group
            command = click.command(name=cmd_name, help=cmd_config["description"])(command_func)
            group.add_command(command)
    
    return cli

def create_command_function(group_name, cmd_name, cmd_config):
    """
    Create a command function based on group and command names.
    
    This function dynamically creates CLI command implementations based on the group and command name.
    
    Args:
        group_name: The command group name (e.g., "subscription")
        cmd_name: The specific command name (e.g., "list", "get")
        cmd_config: The command configuration from cli_config.py
        
    Returns:
        A Click command function that implements the specified command
    """
    
    # Generate a function name
    func_name = f"{group_name}_{cmd_name}"
    
    # Define implementation functions based on command
    
    # Handle subscription list command
    if group_name == "subscription" and cmd_name == "list":
        @pass_context
        def func(ctx):
            """List available Azure subscriptions."""
            try:
                ctx.log("Retrieving subscriptions...", level="debug")
                if not ctx.identity:
                    ctx.log("Identity is not initialized", level="error")
                    return None
                
                ctx.log(f"Identity tenant_id: {ctx.identity.tenant_id}", level="debug")
                subscriptions = ctx.identity.get_subscriptions()
                ctx.log(f"Found {len(subscriptions)} subscriptions", level="debug")
                
                result = [{"name": sub.display_name, "id": sub.subscription_id, "state": sub.state} for sub in subscriptions]
                ctx.output(result, "Available Azure Subscriptions")
                return result
            except Exception as e:
                ctx.log(f"Error listing subscriptions: {str(e)}", level="error")
                import traceback
                ctx.log(traceback.format_exc(), level="debug")
                return None
        return func
            
    # Handle subscription get command
    elif group_name == "subscription" and cmd_name == "get":
        @pass_context
        def func(ctx, subscription_id):
            """Get details of a specific subscription."""
            try:
                ctx.log(f"Getting subscription with ID: {subscription_id}", level="debug")
                subscription = ctx.identity.get_subscription(subscription_id)
                result = {
                    "id": subscription.subscription_id,
                    "name": subscription.subscription.display_name,
                    "state": subscription.subscription.state
                }
                ctx.output(result, f"Subscription: {subscription.subscription.display_name}")
                return result
            except Exception as e:
                ctx.log(f"Error getting subscription details: {str(e)}", level="error")
                import traceback
                ctx.log(traceback.format_exc(), level="debug")
                return None
        return func
    
    # Handle resource-group list command
    elif group_name == "resource-group" and cmd_name == "list":
        @pass_context
        def func(ctx, subscription_id=None):
            """List resource groups in a subscription."""
            try:
                ctx.log("Retrieving resource groups...", level="debug")
                if not ctx.identity:
                    ctx.log("Identity is not initialized", level="error")
                    return None
                
                # Use the provided subscription ID or the default one
                subscription = None
                if subscription_id:
                    ctx.log(f"Using provided subscription ID: {subscription_id}", level="debug")
                    subscription = ctx.identity.get_subscription(subscription_id)
                elif ctx.subscription:
                    ctx.log(f"Using default subscription ID: {ctx.subscription.subscription_id}", level="debug")
                    subscription = ctx.subscription
                else:
                    ctx.log("No subscription ID provided and no default subscription set", level="error")
                    return None
                
                # Get resource groups using the resource_client
                resource_groups = list(subscription.resource_client.resource_groups.list())
                ctx.log(f"Found {len(resource_groups)} resource groups", level="debug")
                
                # Format the result
                result = [
                    {
                        "name": rg.name,
                        "location": rg.location,
                        "provisioning_state": rg.properties.provisioning_state if hasattr(rg, 'properties') and hasattr(rg.properties, 'provisioning_state') else "Unknown"
                    }
                    for rg in resource_groups
                ]
                
                ctx.output(result, f"Resource Groups in Subscription: {subscription.subscription_id}")
                return result
            except Exception as e:
                ctx.log(f"Error listing resource groups: {str(e)}", level="error")
                import traceback
                ctx.log(traceback.format_exc(), level="debug")
                return None
        return func
    
    # Handle resource-group get command
    elif group_name == "resource-group" and cmd_name == "get":
        @pass_context
        def func(ctx, name, subscription_id=None):
            """Get details of a specific resource group."""
            try:
                ctx.log(f"Getting resource group: {name}", level="debug")
                if not ctx.identity:
                    ctx.log("Identity is not initialized", level="error")
                    return None
                
                # Use the provided subscription ID or the default one
                subscription = None
                if subscription_id:
                    ctx.log(f"Using provided subscription ID: {subscription_id}", level="debug")
                    subscription = ctx.identity.get_subscription(subscription_id)
                elif ctx.subscription:
                    ctx.log(f"Using default subscription ID: {ctx.subscription.subscription_id}", level="debug")
                    subscription = ctx.subscription
                else:
                    ctx.log("No subscription ID provided and no default subscription set", level="error")
                    return None
                
                # Get the resource group
                resource_group = subscription.get_resource_group(name)
                if not resource_group:
                    ctx.log(f"Resource group '{name}' not found", level="error")
                    return None
                
                # Format the result
                result = {
                    "name": resource_group.get_name(),
                    "location": resource_group.azure_resource_group.location,
                    "provisioning_state": resource_group.azure_resource_group.properties.provisioning_state if hasattr(resource_group.azure_resource_group, 'properties') and hasattr(resource_group.azure_resource_group.properties, 'provisioning_state') else "Unknown",
                    "id": resource_group.azure_resource_group.id
                }
                
                ctx.output(result, f"Resource Group: {name}")
                return result
            except Exception as e:
                ctx.log(f"Error getting resource group details: {str(e)}", level="error")
                import traceback
                ctx.log(traceback.format_exc(), level="debug")
                return None
        return func
    
    # Handle resource-group create command
    elif group_name == "resource-group" and cmd_name == "create":
        @pass_context
        def func(ctx, name, location, subscription_id=None):
            """Create a new resource group."""
            try:
                ctx.log(f"Creating resource group: {name} in location: {location}", level="debug")
                if not ctx.identity:
                    ctx.log("Identity is not initialized", level="error")
                    return None
                
                # Use the provided subscription ID or the default one
                subscription = None
                if subscription_id:
                    ctx.log(f"Using provided subscription ID: {subscription_id}", level="debug")
                    subscription = ctx.identity.get_subscription(subscription_id)
                elif ctx.subscription:
                    ctx.log(f"Using default subscription ID: {ctx.subscription.subscription_id}", level="debug")
                    subscription = ctx.subscription
                else:
                    ctx.log("No subscription ID provided and no default subscription set", level="error")
                    return None
                
                # Create the resource group
                resource_group = subscription.create_resource_group(name, location)
                
                # Format the result
                result = {
                    "name": resource_group.name,
                    "location": resource_group.location,
                    "provisioning_state": resource_group.properties.provisioning_state if hasattr(resource_group, 'properties') and hasattr(resource_group.properties, 'provisioning_state') else "Unknown",
                    "id": resource_group.id
                }
                
                ctx.log(f"Resource group '{name}' created successfully", level="success")
                ctx.output(result, f"Created Resource Group: {name}")
                return result
            except Exception as e:
                ctx.log(f"Error creating resource group: {str(e)}", level="error")
                import traceback
                ctx.log(traceback.format_exc(), level="debug")
                return None
        return func
    
    # Handle indexer list command
    elif group_name == "indexer" and cmd_name == "list":
        @pass_context
        def func(ctx, search_service, resource_group):
            """List indexers in a search service."""
            try:
                ctx.log(f"Listing indexers in search service: {search_service}", level="debug")
                
                # Get the search service
                if not ctx.subscription:
                    ctx.log("Subscription is not initialized", level="error")
                    return None
                
                # Get the search service
                search_svc = ctx.subscription.get_search_service(search_service)
                if not search_svc:
                    ctx.log(f"Search service '{search_service}' not found", level="error")
                    return None
                
                # Create indexer manager and get indexers
                indexer_manager = search_svc.create_indexer_manager()
                indexers = indexer_manager.get_indexers()
                
                ctx.log(f"Found {len(indexers)} indexers", level="debug")
                
                # Format the result
                result = [
                    {
                        "name": indexer.get_name(),
                        "target_index": indexer.indexer.target_index_name,
                        "data_source": indexer.indexer.data_source_name
                    }
                    for indexer in indexers
                ]
                
                ctx.output(result, f"Indexers in {search_service}")
                return result
            except Exception as e:
                ctx.log(f"Error listing indexers: {str(e)}", level="error")
                import traceback
                ctx.log(traceback.format_exc(), level="debug")
                return None
        return func
    
    # Handle indexer create command
    elif group_name == "indexer" and cmd_name == "create":
        @pass_context
        def func(ctx, name, data_source, target_index, search_service, resource_group, skillset=None, schedule=None):
            """Create an indexer."""
            try:
                ctx.log(f"Creating indexer: {name} in search service: {search_service}", level="debug")
                
                # Get the search service
                if not ctx.subscription:
                    ctx.log("Subscription is not initialized", level="error")
                    return None
                
                # Get the search service
                search_svc = ctx.subscription.get_search_service(search_service)
                if not search_svc:
                    ctx.log(f"Search service '{search_service}' not found", level="error")
                    return None
                
                # Create indexer manager
                indexer_manager = search_svc.create_indexer_manager()
                
                # Check if data source exists
                data_source_obj = indexer_manager.get_data_source_connection(data_source)
                if not data_source_obj:
                    ctx.log(f"Data source '{data_source}' not found", level="error")
                    return None
                
                # Check if target index exists
                index = search_svc.get_index(target_index)
                if not index:
                    ctx.log(f"Target index '{target_index}' not found", level="error")
                    return None
                
                # Process schedule if provided
                indexing_schedule = None
                if schedule:
                    try:
                        # Parse schedule as a cron expression
                        import datetime
                        # Simple parsing for daily/weekly/monthly schedules
                        if schedule.lower() == "daily":
                            indexing_schedule = azsdim.IndexingSchedule(interval=datetime.timedelta(days=1))
                        elif schedule.lower() == "weekly":
                            indexing_schedule = azsdim.IndexingSchedule(interval=datetime.timedelta(days=7))
                        elif schedule.lower() == "monthly":
                            indexing_schedule = azsdim.IndexingSchedule(interval=datetime.timedelta(days=30))
                        else:
                            # Try to parse as hours
                            try:
                                hours = float(schedule)
                                indexing_schedule = azsdim.IndexingSchedule(interval=datetime.timedelta(hours=hours))
                            except ValueError:
                                ctx.log(f"Invalid schedule format: {schedule}. Using default schedule.", level="warning")
                    except Exception as e:
                        ctx.log(f"Error parsing schedule: {str(e)}. Using default schedule.", level="warning")
                
                # Create the indexer
                indexer = indexer_manager.create_indexer(
                    name=name,
                    data_source_name=data_source,
                    target_index_name=target_index,
                    schedule=indexing_schedule
                )
                
                # Format the result
                result = {
                    "name": indexer.get_name(),
                    "target_index": indexer.indexer.target_index_name,
                    "data_source": indexer.indexer.data_source_name,
                    "schedule": str(indexer.indexer.schedule) if indexer.indexer.schedule else "None"
                }
                
                ctx.log(f"Indexer '{name}' created successfully", level="success")
                ctx.output(result, f"Created indexer: {name}")
                return result
            except Exception as e:
                ctx.log(f"Error creating indexer: {str(e)}", level="error")
                import traceback
                ctx.log(traceback.format_exc(), level="debug")
                return None
        return func
    
    # Handle indexer update command
    elif group_name == "indexer" and cmd_name == "update":
        @pass_context
        def func(ctx, name, search_service, resource_group, schedule=None, parameters=None):
            """Update an indexer."""
            try:
                ctx.log(f"Updating indexer: {name} in search service: {search_service}", level="debug")
                
                # Get the search service
                if not ctx.subscription:
                    ctx.log("Subscription is not initialized", level="error")
                    return None
                
                # Get the search service
                search_svc = ctx.subscription.get_search_service(search_service)
                if not search_svc:
                    ctx.log(f"Search service '{search_service}' not found", level="error")
                    return None
                
                # Create indexer manager and get the indexer
                indexer_manager = search_svc.create_indexer_manager()
                indexer = indexer_manager.get_indexer(name)
                
                if not indexer:
                    ctx.log(f"Indexer '{name}' not found", level="error")
                    return None
                
                # Process schedule if provided
                indexing_schedule = None
                if schedule:
                    try:
                        # Parse schedule as a cron expression
                        import datetime
                        # Simple parsing for daily/weekly/monthly schedules
                        if schedule.lower() == "daily":
                            indexing_schedule = azsdim.IndexingSchedule(interval=datetime.timedelta(days=1))
                        elif schedule.lower() == "weekly":
                            indexing_schedule = azsdim.IndexingSchedule(interval=datetime.timedelta(days=7))
                        elif schedule.lower() == "monthly":
                            indexing_schedule = azsdim.IndexingSchedule(interval=datetime.timedelta(days=30))
                        else:
                            # Try to parse as hours
                            try:
                                hours = float(schedule)
                                indexing_schedule = azsdim.IndexingSchedule(interval=datetime.timedelta(hours=hours))
                            except ValueError:
                                ctx.log(f"Invalid schedule format: {schedule}. Schedule not updated.", level="warning")
                    except Exception as e:
                        ctx.log(f"Error parsing schedule: {str(e)}. Schedule not updated.", level="warning")
                
                # Process parameters if provided
                indexing_parameters = None
                if parameters:
                    try:
                        # Parse parameters as JSON
                        params_dict = process_json_arg(parameters)
                        # Convert to IndexingParameters
                        indexing_parameters = azsdim.IndexingParameters(**params_dict)
                    except Exception as e:
                        ctx.log(f"Error parsing parameters: {str(e)}. Parameters not updated.", level="warning")
                
                # Update the indexer
                updated_indexer = indexer.update(
                    schedule=indexing_schedule,
                    parameters=indexing_parameters
                )
                
                # Format the result
                result = {
                    "name": updated_indexer.get_name(),
                    "target_index": updated_indexer.indexer.target_index_name,
                    "data_source": updated_indexer.indexer.data_source_name,
                    "schedule": str(updated_indexer.indexer.schedule) if updated_indexer.indexer.schedule else "None",
                    "parameters": str(updated_indexer.indexer.parameters) if updated_indexer.indexer.parameters else "None"
                }
                
                ctx.log(f"Indexer '{name}' updated successfully", level="success")
                ctx.output(result, f"Updated indexer: {name}")
                return result
            except Exception as e:
                ctx.log(f"Error updating indexer: {str(e)}", level="error")
                import traceback
                ctx.log(traceback.format_exc(), level="debug")
                return None
        return func
    
    # Handle indexer get command
    elif group_name == "indexer" and cmd_name == "get":
        @pass_context
        def func(ctx, name, search_service, resource_group):
            """Get details of a specific indexer."""
            try:
                ctx.log(f"Getting indexer: {name} from search service: {search_service}", level="debug")
                
                # Get the search service
                if not ctx.subscription:
                    ctx.log("Subscription is not initialized", level="error")
                    return None
                
                # Get the search service
                search_svc = ctx.subscription.get_search_service(search_service)
                if not search_svc:
                    ctx.log(f"Search service '{search_service}' not found", level="error")
                    return None
                
                # Create indexer manager and get the indexer
                indexer_manager = search_svc.create_indexer_manager()
                indexer = indexer_manager.get_indexer(name)
                
                if not indexer:
                    ctx.log(f"Indexer '{name}' not found", level="error")
                    return None
                
                # Format the result
                result = {
                    "name": indexer.get_name(),
                    "target_index": indexer.indexer.target_index_name,
                    "data_source": indexer.indexer.data_source_name,
                    "schedule": str(indexer.indexer.schedule) if indexer.indexer.schedule else "None",
                    "parameters": str(indexer.indexer.parameters) if indexer.indexer.parameters else "None"
                }
                
                ctx.output(result, f"Indexer: {name}")
                return result
            except Exception as e:
                ctx.log(f"Error getting indexer details: {str(e)}", level="error")
                import traceback
                ctx.log(traceback.format_exc(), level="debug")
                return None
        return func
    
    # Handle indexer run command
    elif group_name == "indexer" and cmd_name == "run":
        @pass_context
        def func(ctx, name, search_service, resource_group):
            """Run an indexer."""
            try:
                ctx.log(f"Running indexer: {name} in search service: {search_service}", level="debug")
                
                # Get the search service
                if not ctx.subscription:
                    ctx.log("Subscription is not initialized", level="error")
                    return None
                
                # Get the search service
                search_svc = ctx.subscription.get_search_service(search_service)
                if not search_svc:
                    ctx.log(f"Search service '{search_service}' not found", level="error")
                    return None
                
                # Create indexer manager and get the indexer
                indexer_manager = search_svc.create_indexer_manager()
                indexer = indexer_manager.get_indexer(name)
                
                if not indexer:
                    ctx.log(f"Indexer '{name}' not found", level="error")
                    return None
                
                # Run the indexer
                indexer.run()
                
                ctx.log(f"Indexer '{name}' run initiated", level="success")
                return {"status": "success", "message": f"Indexer '{name}' run initiated"}
            except Exception as e:
                ctx.log(f"Error running indexer: {str(e)}", level="error")
                import traceback
                ctx.log(traceback.format_exc(), level="debug")
                return None
        return func
    
    # Handle indexer reset command
    elif group_name == "indexer" and cmd_name == "reset":
        @pass_context
        def func(ctx, name, search_service, resource_group):
            """Reset an indexer."""
            try:
                ctx.log(f"Resetting indexer: {name} in search service: {search_service}", level="debug")
                
                # Get the search service
                if not ctx.subscription:
                    ctx.log("Subscription is not initialized", level="error")
                    return None
                
                # Get the search service
                search_svc = ctx.subscription.get_search_service(search_service)
                if not search_svc:
                    ctx.log(f"Search service '{search_service}' not found", level="error")
                    return None
                
                # Create indexer manager and get the indexer
                indexer_manager = search_svc.create_indexer_manager()
                indexer = indexer_manager.get_indexer(name)
                
                if not indexer:
                    ctx.log(f"Indexer '{name}' not found", level="error")
                    return None
                
                # Reset the indexer
                indexer.reset()
                
                ctx.log(f"Indexer '{name}' reset successful", level="success")
                return {"status": "success", "message": f"Indexer '{name}' reset successful"}
            except Exception as e:
                ctx.log(f"Error resetting indexer: {str(e)}", level="error")
                import traceback
                ctx.log(traceback.format_exc(), level="debug")
                return None
        return func
    
    # Handle indexer status command
    elif group_name == "indexer" and cmd_name == "status":
        @pass_context
        def func(ctx, name, search_service, resource_group):
            """Get indexer status."""
            try:
                ctx.log(f"Getting status for indexer: {name} in search service: {search_service}", level="debug")
                
                # Get the search service
                if not ctx.subscription:
                    ctx.log("Subscription is not initialized", level="error")
                    return None
                
                # Get the search service
                search_svc = ctx.subscription.get_search_service(search_service)
                if not search_svc:
                    ctx.log(f"Search service '{search_service}' not found", level="error")
                    return None
                
                # Create indexer manager and get the indexer
                indexer_manager = search_svc.create_indexer_manager()
                indexer = indexer_manager.get_indexer(name)
                
                if not indexer:
                    ctx.log(f"Indexer '{name}' not found", level="error")
                    return None
                
                # Get the status
                status = indexer.get_status()
                
                # Format the result
                result = {
                    "status": status.status,
                    "last_run": str(status.last_execution_time) if hasattr(status, 'last_execution_time') else "Never",
                    "document_count": status.document_count if hasattr(status, 'document_count') else 0,
                    "success_count": status.success_document_count if hasattr(status, 'success_document_count') else 0,
                    "error_count": status.failed_document_count if hasattr(status, 'failed_document_count') else 0
                }
                
                ctx.output(result, f"Status for indexer: {name}")
                return result
            except Exception as e:
                ctx.log(f"Error getting indexer status: {str(e)}", level="error")
                import traceback
                ctx.log(traceback.format_exc(), level="debug")
                return None
        return func
    
    # Handle indexer delete command
    elif group_name == "indexer" and cmd_name == "delete":
        @pass_context
        def func(ctx, name, search_service, resource_group, force=False):
            """Delete an indexer."""
            try:
                ctx.log(f"Deleting indexer: {name} from search service: {search_service}", level="debug")
                
                # Get the search service
                if not ctx.subscription:
                    ctx.log("Subscription is not initialized", level="error")
                    return None
                
                # Get the search service
                search_svc = ctx.subscription.get_search_service(search_service)
                if not search_svc:
                    ctx.log(f"Search service '{search_service}' not found", level="error")
                    return None
                
                # Create indexer manager and get the indexer
                indexer_manager = search_svc.create_indexer_manager()
                indexer = indexer_manager.get_indexer(name)
                
                if not indexer:
                    ctx.log(f"Indexer '{name}' not found", level="error")
                    return None
                
                # Confirm deletion if force is not set
                if not force:
                    if not click.confirm(f"Are you sure you want to delete indexer '{name}'?"):
                        ctx.log("Deletion cancelled", level="info")
                        return {"status": "cancelled", "message": "Deletion cancelled"}
                
                # Delete the indexer
                indexer.delete()
                
                ctx.log(f"Indexer '{name}' deleted successfully", level="success")
                return {"status": "success", "message": f"Indexer '{name}' deleted successfully"}
            except Exception as e:
                ctx.log(f"Error deleting indexer: {str(e)}", level="error")
                import traceback
                ctx.log(traceback.format_exc(), level="debug")
                return None
        return func
    
    # Default handler for all other commands
    else:
        # Default fallback function for any unimplemented command
        @pass_context
        def func(ctx, **kwargs):
            """Auto-generated handler for the command."""
            # Show which command was tried
            cmd_path = f"{group_name} {cmd_name}"
            
            ctx.log(f"Command {cmd_path} not fully implemented yet", level="error")
            ctx.log(f"Command arguments: {kwargs}", level="debug")
            
            # Show a helpful message about available commands
            ctx.log("Available commands: subscription list, subscription get, resource-group list, resource-group get, resource-group create, indexer list, indexer get, indexer create, indexer run, indexer reset, indexer status, indexer update, indexer delete", level="info")
            return None
            
        # Set the function name for better debugging
        func.__name__ = func_name
        return func

def main():
    """Main entry point for the azwrap CLI."""
    try:
        cli = create_cli()
        return cli(standalone_mode=False)
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1

if __name__ == "__main__":
    main()