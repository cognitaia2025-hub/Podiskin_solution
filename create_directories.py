import os

# Create directory structure
dirs = [
    'Frontend/src/pages/admin',
    'Frontend/src/components/admin',
    'backend/users'
]

for d in dirs:
    os.makedirs(d, exist_ok=True)
    print(f"✓ Created: {d}")

print("\nDirectory structure ready!")
