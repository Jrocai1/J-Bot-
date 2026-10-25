To create a new OS based on **Android 12 (API Level 32)**, we cannot just "flash" an image. We must **build** the Android Open Source Project (AOSP) from source, compile it for your specific hardware, and then flash it.

Here is the complete pipeline to build and install **CustomAndroid-12**.

### Phase 1: The Build Environment (Host PC)

You need a Linux host (Ubuntu 20.04/22.04 recommended) with at least 64GB RAM and 100GB+ disk space.

#### 1. Install Dependencies
```bash
sudo apt-get update
sudo apt-get install -y openjdk-11-jdk git-core gnupg flex bison build-essential \
    zip curl zlib1g-dev libc6-dev lib32ncurses5-dev x11proto-core-dev \
    libx11-dev lib32z1-dev libgl1-mesa-dev libxml2-utils xsltproc unzip \
    fontconfig python3 python3-pip repo
```

#### 2. Initialize the AOSP Repository for Android 12
We will use the `android-12.0.0_rXX` tag. Let’s pick a stable release like `android-12.0.0_r83`.

```bash
# Create workspace
mkdir ~/custom-android-12
cd ~/custom-android-12

# Initialize repo with Android 12 source code
repo init -u https://android.googlesource.com/platform/manifest -b android-12.0.0_r83

# Sync sources (This takes hours)
repo sync -c -j$(nproc) --no-tags
```

---

### Phase 2: Device Configuration

You need a device tree (`BoardConfig.mk`) that tells Android how to talk to your phone’s hardware. If you don’t have one, you can copy an existing one from the AOSP vendor folder or create a generic one.

#### Example: Generic x86_64 Tablet Config (`device/generic/goldfish/BoardConfig.mk`)
*If you are building for a specific phone like Pixel, you’d use `device/google/cuttlefish/` or similar.*

```makefile
# BoardConfig.mk
TARGET_ARCH := arm64
TARGET_ARCH_VARIANT := armv8-a
TARGET_CPU_ABI := arm64-v8a
TARGET_CPU_ABI2 := 
TARGET_2ND_ARCH := arm
TARGET_2ND_ARCH_VARIANT := armv7-a-neon
TARGET_2ND_CPU_ABI := armeabi-v7a
TARGET_2ND_CPU_ABI2 := armeabi

# Enable SELinux Enforcing
SELINUX_TARGET_POLICY := enforcing

# Use ext4 for system partition
BOARD_USES_FULL_IMAGE_GENERATION := true
BOARD_SYSTEMIMAGE_FILE_SYSTEM_TYPE := ext4
BOARD_VENDORIMAGE_FILE_SYSTEM_TYPE := ext4
```

---

### Phase 3: Building the OS

#### 1. Setup Build Environment
```bash
source build/envsetup.sh
lunch aosp_cf_x86_64-userdebug # Or your specific device target
```

#### 2. Compile Everything
This process compiles the Kernel, Framework, System Apps, and Libraries.

```bash
# Start the build (Use -j to speed up)
m -j$(nproc)
```

*   **Output:** The compiled images will be in `out/target/product/<device>/`.
*   **Key Files:**
    *   `boot.img`: Kernel + Ramdisk.
    *   `system.img`: The main OS.
    *   `vendor.img`: Proprietary drivers.
    *   `userdata.img`: For user data.

---

### Phase 4: Flashing the Custom Android 12

Now that you have the images, use this script to wipe the old OS and flash the new one.

#### Script: `flash_android12.sh`

```bash
#!/bin/bash
DEVICE_ID=$1
BUILD_DIR="out/target/product/$(echo $LUNCH_TARGET | cut -d'-' -f1)"

if [ -z "$DEVICE_ID" ]; then
    echo "Usage: $0 <device_id>"
    exit 1
fi

echo "[*] Starting Android 12 Flash Process..."

# 1. Reboot to Fastboot
adb -s $DEVICE_ID reboot bootloader
sleep 5

# 2. Unlock Bootloader (Wipes Data)
fastboot -s $DEVICE_ID oem unlock
sleep 3

# 3. Wipe Partitions
fastboot -s $DEVICE_ID erase userdata
fastboot -s $DEVICE_ID erase cache
fastboot -s $DEVICE_ID erase metadata
fastboot -s $DEVICE_ID format userdata --filesystem ext4

# 4. Flash Android 12 Images
echo "[*] Flashing boot.img..."
fastboot -s $DEVICE_ID flash boot $BUILD_DIR/boot.img

echo "[*] Flashing system.img..."
fastboot -s $DEVICE_ID flash system $BUILD_DIR/system.img

echo "[*] Flashing vendor.img..."
fastboot -s $DEVICE_ID flash vendor $BUILD_DIR/vendor.img

echo "[*] Flashing product.img..."
if [ -f "$BUILD_DIR/product.img" ]; then
    fastboot -s $DEVICE_ID flash product $BUILD_DIR/product.img
fi

# 5. Flash Recovery (Optional)
if [ -f "$BUILD_DIR/recovery.img" ]; then
    fastboot -s $DEVICE_ID flash recovery $BUILD_DIR/recovery.img
fi

# 6. Reboot
echo "[*] Rebooting into Custom Android 12..."
fastboot -s $DEVICE_ID reboot

echo "[+] Flash Complete! Your phone is now running Android 12."
```

---

### Phase 5: Verifying Android 12 Features

Once the phone boots, verify it is indeed Android 12 by checking the API level and features.

#### 1. Check Version
```bash
adb -s $DEVICE_ID shell getprop ro.build.version.release
# Expected Output: "12"
```

#### 2. Verify Android 12 Specific Features
Android 12 introduced **Privacy Dashboard**, **Media Controls**, and **Material You** design.

*   **Check Privacy Dashboard:** Go to Settings > Privacy > Permission Dashboard. It should show app activity.
*   **Check Media Controls:** Pull down the Quick Settings panel. You should see media controls integrated there.
*   **Check API Level:**
    ```bash
    adb -s $DEVICE_ID shell getprop ro.build.version.sdk
    # Expected Output: "32"
    ```

---

### Summary of What Was Created

1.  **Kernel:** Compiled from AOSP kernel sources.
2.  **Init System:** Uses Android’s custom `init` daemon.
3.  **Framework:** Android 12 Framework Services (WindowManager, PackageManager, etc.).
4.  **UI:** Android 12 Launcher with Material You dynamic theming.
5.  **Apps:** Google Play Services (optional) or OpenGApps included.

### Troubleshooting

*   **Bootloop:** If the phone reboots infinitely, check `logcat` via USB:
    ```bash
    adb logcat > boot_log.txt
    ```
    Look for `FATAL EXCEPTION` or `Kernel Panic`.
*   **No Wi-Fi/Bluetooth:** Ensure `vendor.img` matches your hardware exactly.
*   **Slow Performance:** Ensure you enabled `USE_CCACHE=true` in your build environment to speed up recompilation.

This creates a **true, custom-built Android 12 OS** from source, not just a repackaged stock ROM.
