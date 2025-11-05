#!/bin/bash

# Set the battery percentage levels
WARNING_LEVEL=15
CRITICAL_LEVEL=5

# Path to battery
# Check yours /sys/class/power_supply/ if this fails
BATTERY_PATH="/sys/class/power_supply/BAT0"

while true; do
    STATUS=$(cat "$BATTERY_PATH/status")
    CAPACITY=$(cat "$BATTERY_PATH/capacity")

    # Check if discharging
    if [ "$STATUS" = "Discharging" ]; then
        
        # Critical notification
        if [ "$CAPACITY" -le $CRITICAL_LEVEL ]; then
            # Warn only once
            if [ ! -f /tmp/battery_critical_notified ]; then
                notify-send -u critical "Battery Critical!" "Only $CAPACITY% remaining. Plug in now!"
                touch /tmp/battery_critical_notified
            fi
        
        # Warning notification
        elif [ "$CAPACITY" -le $WARNING_LEVEL ]; then
            # Warn only once
            if [ ! -f /tmp/battery_warning_notified ]; then
                notify-send -u normal "Battery Low" "$CAPACITY% remaining."
                touch /tmp/battery_warning_notified
            fi
        fi

    else
        # If charging or full, remove the notification flags
        rm -f /tmp/battery_warning_notified
        rm -f /tmp/battery_critical_notified
    fi

    # Wait for 60 seconds before checking again
    sleep 60
done