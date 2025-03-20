import os
import time
import shutil
import psutil
import subprocess
from pathlib import Path

def open_directory(path):
    """Open the directory in the file explorer."""
    print(f"Opening directory: {path}")
    
    if os.name == 'nt':  # Windows
        os.startfile(path)
    elif os.name == 'posix':  # Linux, macOS
        if os.path.exists('/usr/bin/xdg-open'):  # Linux
            subprocess.call(['xdg-open', path])
        else:  # macOS
            subprocess.call(['open', path])
    
    # Wait a moment to let the explorer window open
    time.sleep(1)

def detect_new_drives():
    """Detect newly connected drives."""
    old_drives = set()
    
    print("Waiting for USB drive to be connected...")
    while True:
        drives = set()
        
        # Get all drives
        for partition in psutil.disk_partitions():
            # Skip system drives (on Windows) and non-removable drives
            if 'removable' in partition.opts.lower() or (os.name != 'nt' and partition.mountpoint.startswith('/media')):
                drives.add(partition.mountpoint)
        
        # Check for new drives
        new_drives = drives - old_drives
        if new_drives:
            return list(new_drives)[0]  # Return the first new drive
        
        old_drives = drives
        time.sleep(1)  # Check every second

def enable_long_paths():
    """
    Try to enable long path support on Windows
    Note: This requires admin rights and Windows 10/11
    """
    if os.name == 'nt':
        try:
            import winreg
            key = winreg.HKEY_LOCAL_MACHINE
            subkey = r"SYSTEM\CurrentControlSet\Control\FileSystem"
            with winreg.OpenKey(key, subkey, 0, winreg.KEY_WRITE) as registry_key:
                winreg.SetValueEx(registry_key, "LongPathsEnabled", 0, winreg.REG_DWORD, 1)
            print("Long path support enabled. You may need to restart your computer.")
        except Exception as e:
            print(f"Could not enable long path support: {e}")
            print("Script will continue but may hit path length limitations.")

def organize_drive_contents(drive_path):
    """Organize drive contents into 260 nested folders."""
    current_dir = Path(drive_path)
    
    print(f"Starting organization process on drive: {current_dir}")
    
    # Open the original drive directory
    open_directory(current_dir)
    time.sleep(1)  # Give time to view
    
    # Continue creating folders until we reach 260 levels or hit an error
    level = 1
    max_levels = 260
    
    while level <= max_levels:
        # Create the new directory for this level
        new_dir = current_dir / str(level)
        
        print(f"Level {level}: Processing directory {current_dir}")
        
        # Get all files and folders in the current directory, excluding the folder we're about to create
        items = [item for item in current_dir.glob('*') if item.name != str(level)]
        
        if not items and level > 1:
            print(f"No items found in {current_dir}. Creating empty folder and continuing.")
            
        try:
            # Create the new directory
            print(f"Creating directory: {new_dir}")
            new_dir.mkdir(exist_ok=True)
            
            # Move all items to the new directory
            if items:
                print(f"Moving {len(items)} items to {new_dir}")
                for item in items:
                    # Destination path
                    dest = new_dir / item.name
                    
                    # Handle existing files at destination
                    if dest.exists():
                        print(f"Warning: {dest} already exists. Skipping {item}")
                        continue
                        
                    try:
                        # Using shutil.move which works for both files and directories
                        shutil.move(str(item), str(new_dir))
                        print(f"Moved: {item.name} -> {new_dir}")
                    except Exception as e:
                        print(f"Error moving {item}: {e}")
            
            # Open the new directory
            open_directory(new_dir)
            
            # Update current directory for next iteration
            current_dir = new_dir
            level += 1
            
        except Exception as e:
            print(f"Error at level {level}: {e}")
            print(f"Reached maximum practical depth at {level-1} levels.")
            break
    
    print(f"Process completed. Created {level-1} levels of nested folders.")

if __name__ == "__main__":
    try:
        # Try to enable long path support on Windows
        if os.name == 'nt':
            enable_long_paths()
        
        # Wait for a USB drive to be connected
        drive_path = detect_new_drives()
        print(f"USB drive detected at: {drive_path}")
        
        # Organize the contents with up to 260 levels
        organize_drive_contents(drive_path)
        
    except KeyboardInterrupt:
        print("\nProcess interrupted by user.")
    except Exception as e:
        print(f"An error occurred: {e}")