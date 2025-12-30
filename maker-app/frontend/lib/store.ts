/**
 * Global State Management with Zustand
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface User {
  brand_id: number;
  email?: string;
  name?: string;
}

interface TokenBalance {
  balance: number;
  total_earned: number;
  total_spent: number;
}

interface Subscription {
  tier: string;
  status: string;
  monthly_tokens: number;
}

interface AppState {
  // Auth
  user: User | null;
  authToken: string | null;
  setAuth: (token: string, user: User) => void;
  clearAuth: () => void;

  // Tokens & Billing
  tokenBalance: TokenBalance | null;
  subscription: Subscription | null;
  setTokenBalance: (balance: TokenBalance) => void;
  setSubscription: (sub: Subscription) => void;

  // Printify
  printifyToken: string | null;
  printifyShopId: number | null;
  setPrintify: (token: string, shopId: number) => void;
  clearPrintify: () => void;

  // UI State
  sidebarOpen: boolean;
  toggleSidebar: () => void;

  // Generation Queue
  activeJobs: number[];
  addJob: (jobId: number) => void;
  removeJob: (jobId: number) => void;
}

export const useStore = create<AppState>()(
  persist(
    (set) => ({
      // Auth
      user: null,
      authToken: null,
      setAuth: (token, user) => {
        if (typeof window !== 'undefined') {
          localStorage.setItem('auth_token', token);
        }
        set({ authToken: token, user });
      },
      clearAuth: () => {
        if (typeof window !== 'undefined') {
          localStorage.removeItem('auth_token');
        }
        set({ authToken: null, user: null });
      },

      // Tokens & Billing
      tokenBalance: null,
      subscription: null,
      setTokenBalance: (balance) => set({ tokenBalance: balance }),
      setSubscription: (sub) => set({ subscription: sub }),

      // Printify
      printifyToken: null,
      printifyShopId: null,
      setPrintify: (token, shopId) => {
        if (typeof window !== 'undefined') {
          localStorage.setItem('printify_token', token);
          localStorage.setItem('printify_shop_id', shopId.toString());
        }
        set({ printifyToken: token, printifyShopId: shopId });
      },
      clearPrintify: () => {
        if (typeof window !== 'undefined') {
          localStorage.removeItem('printify_token');
          localStorage.removeItem('printify_shop_id');
        }
        set({ printifyToken: null, printifyShopId: null });
      },

      // UI State
      sidebarOpen: true,
      toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),

      // Generation Queue
      activeJobs: [],
      addJob: (jobId) => set((state) => ({ activeJobs: [...state.activeJobs, jobId] })),
      removeJob: (jobId) =>
        set((state) => ({ activeJobs: state.activeJobs.filter((id) => id !== jobId) })),
    }),
    {
      name: 'maker-storage',
      partialize: (state) => ({
        user: state.user,
        authToken: state.authToken,
        printifyToken: state.printifyToken,
        printifyShopId: state.printifyShopId,
      }),
    }
  )
);
