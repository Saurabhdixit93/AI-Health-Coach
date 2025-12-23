/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        "whatsapp-green": "#25D366",
        "whatsapp-light": "#E7FFDB",
        "whatsapp-dark": "#075E54",
        "message-user": "#DCF8C6",
        "message-ai": "#FFFFFF",
      },
      boxShadow: {
        message: "0 1px 0.5px rgba(0,0,0,0.13)",
      },
    },
  },
  plugins: [],
};
