import type { AppProps } from 'next/app';
import Head from 'next/head';
import { useEffect } from 'react';
import '../styles/globals.css';
import { useStore } from '../lib/store';
import { rewardsAPI, billingAPI } from '../lib/api';

export default function App({ Component, pageProps }: AppProps) {
  const { authToken, setTokenBalance, setSubscription } = useStore();

  // Load user data on mount
  useEffect(() => {
    if (authToken) {
      // Fetch token balance
      rewardsAPI.getBalance()
        .then(res => setTokenBalance(res.data))
        .catch(console.error);

      // Fetch subscription
      billingAPI.getSubscription()
        .then(res => setSubscription(res.data))
        .catch(console.error);
    }
  }, [authToken, setTokenBalance, setSubscription]);

  return (
    <>
      <Head>
        <title>StaticWaves Maker - AI Content Creation</title>
        <meta name="description" content="Create images, videos, music, and books with AI. Sell prints and merch." />
        <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no, viewport-fit=cover" />
        <meta name="theme-color" content="#7B2CFF" />
        <link rel="manifest" href="/manifest.json" />
        <link rel="icon" href="/favicon.ico" />
        <link rel="apple-touch-icon" href="/icon-192.png" />
      </Head>
      <Component {...pageProps} />
    </>
  );
}
