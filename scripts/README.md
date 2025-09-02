# Screen Wake Management Scripts

This directory contains scripts to manage screen sleep behavior during development work.

## Scripts

### keep_awake.sh
Keeps the display awake for a specified duration using macOS's built-in `caffeinate` utility.

**Usage:**
```bash
./keep_awake.sh [duration_in_seconds]
```

- Default duration is 60 minutes (3600 seconds) if no duration is specified
- The script starts caffeinate in the background and reports the process ID

**Examples:**
```bash
# Keep awake for 30 minutes
./keep_awake.sh 1800

# Keep awake for 60 minutes (default)
./keep_awake.sh

# Keep awake for 2 hours
./keep_awake.sh 7200
```

### stop_awake.sh
Stops all running caffeinate processes.

**Usage:**
```bash
./stop_awake.sh
```

## Aliases

After sourcing `.zshrc`, the following aliases are available:

- `keep-awake` - Equivalent to `./keep_awake.sh`
- `stop-awake` - Equivalent to `./stop_awake.sh`

## Manual caffeinate commands

You can also use caffeinate directly:

```bash
# Keep display awake for 1 hour
caffeinate -u -t 3600 &

# Keep display awake indefinitely (until process is killed)
caffeinate -u &

# Kill caffeinate processes
pkill caffeinate
```

## Best Practices

1. Always use `keep_awake.sh` or `keep-awake` alias before starting work sessions
2. Use `stop_awake.sh` or `stop-awake` alias when work is complete to restore normal energy saving
3. Specify appropriate durations to balance productivity with energy efficiency
4. Default 60-minute duration is suitable for most work sessions