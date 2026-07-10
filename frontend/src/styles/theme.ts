export const theme = {
  colors: {
    brand: {
      primary: '#4f46e5',
      primaryHover: '#4338ca',
      light: '#eef2ff',
    },
    surface: {
      bg: '#f8fafc',
      card: '#ffffff',
      border: '#e2e8f0',
    },
    text: {
      primary: '#0f172a',
      muted: '#64748b',
    },
  },
  layout: {
    sidebarWidth: '16rem',
    navbarHeight: '4rem',
  },
} as const

export type Theme = typeof theme
