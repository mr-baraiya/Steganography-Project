# Google Play Store Publishing Guide - CELATUS

This document provides a comprehensive step-by-step walkthrough for publishing **CELATUS** to the **Google Play Store**.

---

## 1. Prerequisites

Before uploading CELATUS to the Google Play Store, prepare the following:
1. **Google Play Developer Account**: Sign up at [play.google.com/console](https://play.google.com/console/signup) ($25 one-time registration fee).
2. **Android App Bundle File**: Use `downloads/celatus_mobile.aab` created in this repository.
3. **High-Resolution App Icon**: `assets/icon-512.png` (512x512 PNG).
4. **Feature Graphic**: 1024x500 PNG/JPEG banner.
5. **App Screenshots**: 2 or more phone screenshots (min 320px, max 3840px).

---

## 2. Step-by-Step Google Play Console Setup

### Step 1: Create a New Application
1. Log into your [Google Play Console](https://play.google.com/console).
2. Click **Create app** on the top right.
3. Fill in the App Details:
   - **App Name**: `CELATUS - Image Steganography Studio`
   - **Default Language**: English (United States)
   - **App or Game**: App
   - **Free or Paid**: Free
4. Accept the Declarations and click **Create app**.

---

### Step 2: Upload the App Package (.aab)
1. In the left menu, select **Production** (or **Testing** > **Internal testing** for a dry run).
2. Click **Create new release**.
3. Under **App bundles**, click **Upload** and select `downloads/celatus_mobile.aab` (or `downloads/celatus_mobile.apk`).
4. Enter Release Notes:
   ```text
   Initial release of CELATUS Image Steganography Studio for Android.
   - LSB image channel message encoding & decoding
   - 16-bit passcode key checksum protection
   - 100% offline image processing
   ```
5. Click **Save** then **Next**.

---

### Step 3: Set Up Store Listing Details
1. Go to **Grow** > **Store presence** > **Main store listing**.
2. **Short Description** (max 80 chars):
   `Hide secret encrypted text messages inside carrier images securely.`
3. **Full Description**:
   ```text
   CELATUS is a powerful image steganography application designed for covert data protection and privacy.

   FEATURES:
   • LSB Encoding: Hide UTF-8 text payloads undetected inside PNG and JPEG images.
   • Passcode Key Protection: Guard payloads with a 16-bit hash passcode.
   • Protocol Verification: 10-byte binary header validation ensures accurate payload extraction.
   • 100% Offline: All image processing runs locally on your device for absolute privacy.
   ```
4. **Graphics**:
   - **App Icon**: Upload `assets/icon-512.png`
   - **Feature Graphic**: Upload a 1024x500 banner image.
   - **Phone Screenshots**: Upload at least 2 screenshots of the app in action.

---

### Step 4: Complete App Content Declarations
Under **Policy and programs** > **App content**, complete all mandatory sections:
1. **Privacy Policy**: Enter the URL of your hosted privacy policy (e.g., `https://mr-baraiya.github.io/Steganography-Project/`).
2. **Ads**: Select "No, my app does not contain ads".
3. **Content Ratings**: Fill out the questionnaire (Targeted at 13+ or General Audience, Utility/Security category).
4. **Target Audience**: Select 13+ / 18+.
5. **News Apps & COVID-19 Declarations**: Select "No".

---

### Step 5: Submit for Review
1. Go back to **Production** > **Releases**.
2. Click **Edit release** > **Review release**.
3. Confirm all details and click **Start roll-out to Production**.
4. Google usually reviews new app submissions within **24 to 72 hours**. Once approved, CELATUS will be live on the Google Play Store!

---

## 3. Alternative Direct Installation (Sideloading .APK)

If users prefer installing the mobile app directly without Google Play:
1. Transfer `downloads/celatus_mobile.apk` to an Android phone.
2. Tap the `.apk` file in File Manager.
3. Allow **"Install from Unknown Sources"** if prompted by Android.
4. Tap **Install** to enjoy native mobile CELATUS!
