import type { CapacitorConfig } from '@capacitor/cli';

// Thin native shell around the live web app. The UI is served from GitHub
// Pages, so any change committed to the HIE-Calculator repo reaches this app
// the next time it is opened — no rebuild, no Play upload. This bundle exists
// only to (a) meet Google Play's target-API requirement and (b) give us a
// signing key we control going forward.
const config: CapacitorConfig = {
  appId: 'com.hiecalc',
  appName: 'HIE Calculator',
  webDir: 'www',
  server: {
    // The published UI. Must stay in sync with the app's Play listing.
    url: 'https://nncceducation-cpu.github.io/HIE-Calculator/',
    androidScheme: 'https',
    // only our own https origin is allowed; no cleartext
    allowNavigation: ['nncceducation-cpu.github.io'],
  },
};

export default config;
