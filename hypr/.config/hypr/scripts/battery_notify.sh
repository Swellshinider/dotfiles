#!/bin/bash

# Set the battery percentage levels
WARNING_LEVEL=20
CRITICAL_LEVEL=10

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
            if [ ! -f /tmp/battery_critical_notified ]; then
                notify-send --app-name="System Notification" --icon="$HOME/.config/hypr/images/empty-battery.png" --urgency=critical "Battery Critical!" "Only $CAPACITY% remaining. Plug in now!"
                touch /tmp/battery_critical_notified
            fi
        
        # Warning notification
        elif [ "$CAPACITY" -le $WARNING_LEVEL ]; then
            if [ ! -f /tmp/battery_warning_notified ]; then
                notify-send --app-name="System Notification" --icon="$HOME/.config/hypr/images/low-battery.png" --urgency=normal "Battery Low!" "$CAPACITY% remaining. Please consider plugging in."
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