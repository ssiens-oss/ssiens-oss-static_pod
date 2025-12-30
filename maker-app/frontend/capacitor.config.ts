import { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'com.staticwaves.maker',
  appName: 'StaticWaves Maker',
  webDir: 'out',
  bundledWebRuntime: false,
  server: {
    androidScheme: 'https',
    hostname: 'maker.app',
    iosScheme: 'ionic'
  },
  plugins: {
    AdMob: {
      appId: 'ca-app-pub-3940256099942544~3347511713', // Test ID - replace with yours
      testingDevices: ['YOUR_DEVICE_ID'],
      initializeForTesting: true
    },
    SplashScreen: {
      launchShowDuration: 2000,
      backgroundColor: '#050507',
      androidScaleType: 'CENTER_CROP',
      showSpinner: false
    },
    StatusBar: {
      style: 'dark',
      backgroundColor: '#050507'
    }
  },
  android: {
    allowMixedContent: false,
    captureInput: true,
    webContentsDebuggingEnabled: false,
    // Optimized for Samsung S25 Ultra (QHD+ display)
    buildOptions: {
      keystorePath: undefined,
      keystorePassword: undefined,
      keystoreAlias: undefined,
      keystoreAliasPassword: undefined,
      releaseType: 'APK'
    }
  }
};

export default config;
