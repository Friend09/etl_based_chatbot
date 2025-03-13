# Logger Migration Guide

This guide helps you migrate your existing logger references (`logger = logging.getLogger(__name__)`) to our new comprehensive logging system.

## Migration Options

### Option 1: Automated Migration

The quickest way to update all your modules is to use the `logger_migration.py` utility:

1. Create the required directories and files first:

   ```bash
   mkdir -p utils logs
   ```

2. Run the migration script:

   ```python
   python -m utils.logger_migration
   ```

3. Review the changes made to your files.

### Option 2: Manual Migration

If you prefer to update your files manually, follow these steps for each Python module:

1. Find all instances of logger initialization:

   ```python
   import logging
   logger = logging.getLogger(__name__)
   ```

2. Replace with the appropriate component logger:

   ```python
   from utils import get_component_logger
   logger = get_component_logger('component_type', 'module_name')
   ```

3. Choose the appropriate component type based on the module's location:
   - `'etl'` for modules in the etl directory
   - `'web'` for modules in the web directory
   - `'db'` for modules in the database directory
   - `'app'` for any other modules

### Option 3: Hybrid Approach

For a more controlled migration:

1. Update critical modules manually
2. Run the automated migration for remaining modules
3. Test each component thoroughly after migration

## Example Migration

### Before:

```python
# etl/weather_collector.py
import logging
import requests

logger = logging.getLogger(__name__)

def get_weather(location):
    logger.info(f"Getting weather for {location}")
    # Implementation...
```

### After:

```python
# etl/weather_collector.py
import requests
from utils import get_component_logger, log_etl_function

logger = get_component_logger('etl', 'weather_collector')

@log_etl_function
def get_weather(location):
    logger.info(f"Getting weather for {location}")
    # Implementation...
```

## Migration Checklist

For each module:

- [ ] Update the import statements
- [ ] Replace the logger initialization
- [ ] Add function decorators where appropriate
- [ ] Verify log output in the correct log files
- [ ] Ensure sensitive data is properly masked

## Verifying Migration Success

After migration, verify that:

1. All log files are created in the `logs` directory
2. Log entries contain the expected contextual information
3. Sensitive data is properly masked in the logs
4. Component-specific logs go to the appropriate files
5. Function entry/exit is logged where decorators are used

## Troubleshooting

If you encounter issues:

- Check that all required directories exist (logs, utils)
- Verify that your PYTHONPATH includes the project root
- Check file permissions for log file writing
- Ensure no duplicate logger configurations exist

For additional help, refer to the full logging system documentation.
