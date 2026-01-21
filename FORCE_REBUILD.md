# Force Rebuild

Render is caching old code. To fix:

## Option 1: Clear Build Cache
1. Go to telegram-bot-worker service
2. Settings tab
3. Find "Clear build cache" button
4. Click it
5. Then Manual Deploy

## Option 2: Delete and Recreate Service
Since cache is stubborn, delete the service completely and create fresh.
