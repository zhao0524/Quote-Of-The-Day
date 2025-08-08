# Quote of the Day App

A beautiful, responsive web application that displays daily inspirational quotes using the ZenQuotes API. Built with React, TypeScript, and Tailwind CSS.

## 🌟 Features

### Core Functionality
- **Daily Quote Display**: Fetches and displays random inspirational quotes from ZenQuotes API
- **Author Attribution**: Shows the author of each quote
- **Refresh Functionality**: Get new quotes on demand

### Enhanced Features
- **Dark/Light Mode Toggle**: Switch between dark and light themes
- **Share Quotes**: Share quotes via native sharing API or copy to clipboard
- **Loading States**: Smooth loading animations and error handling
- **Responsive Design**: Optimized for desktop, tablet, and mobile devices
- **Smooth Animations**: Elegant transitions and hover effects
- **Error Handling**: Graceful error handling with retry functionality

### Technical Features
- **TypeScript**: Full type safety and better development experience
- **Tailwind CSS**: Utility-first CSS framework for rapid UI development
- **Modern React**: Built with functional components and hooks
- **API Integration**: Seamless integration with ZenQuotes API
- **Accessibility**: Keyboard navigation and screen reader friendly

## 🚀 Getting Started

### Prerequisites
- Node.js (version 14 or higher)
- npm or yarn package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/Quote-Of-The-Day.git
   cd Quote-Of-The-Day
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start the development server**
   ```bash
   npm start
   ```

4. **Open your browser**
   Navigate to `http://localhost:3000` to view the application

### Building for Production

```bash
npm run build
```

This creates an optimized production build in the `build` folder.

## 🛠️ Technology Stack

- **Frontend Framework**: React 19.1.1
- **Language**: TypeScript 4.9.5
- **Styling**: Tailwind CSS 3.x
- **Build Tool**: Create React App
- **API**: ZenQuotes API (https://zenquotes.io/)

## 📱 Usage

1. **View Daily Quote**: The app automatically loads a random quote when opened
2. **Get New Quote**: Click the "New Quote" button to fetch a different quote
3. **Share Quote**: Use the "Share Quote" button to share via native sharing or copy to clipboard
4. **Toggle Theme**: Switch between dark and light modes using the theme toggle button

## 🎨 Design Decisions

### UI/UX Choices
- **Clean, Minimal Design**: Focus on readability and content
- **Card-based Layout**: Modern card design with subtle shadows and rounded corners
- **Responsive Typography**: Scalable text sizes for different screen sizes
- **Color Psychology**: Blue theme for trust and inspiration, with proper contrast ratios
- **Smooth Transitions**: Subtle animations enhance user experience without being distracting

### Technical Decisions
- **TypeScript**: Chosen for type safety and better development experience
- **Tailwind CSS**: Utility-first approach for rapid development and consistent styling
- **Functional Components**: Modern React patterns with hooks for state management
- **Error Boundaries**: Proper error handling for better user experience
- **Progressive Enhancement**: Works without JavaScript for basic functionality

## 🔧 API Integration

The app integrates with multiple quote APIs with automatic fallback:
- **Primary**: Quotable API (`https://api.quotable.io/random`)
- **Fallback 1**: ZenQuotes API via CORS proxy
- **Fallback 2**: Quotes REST API (`https://quotes.rest/qod`)
- **Response Format**: Normalized to `{ q: string, a: string }` format
- **Error Handling**: Graceful fallback between APIs
- **CORS Handling**: Uses multiple APIs to avoid CORS restrictions

## 📁 Project Structure

```
src/
├── App.tsx          # Main application component
├── App.css          # Custom styles and animations
├── index.tsx        # Application entry point
└── index.css        # Global styles and Tailwind imports
```

## 🚀 Deployment

The app can be deployed to any static hosting service:

- **Netlify**: Drag and drop the `build` folder
- **Vercel**: Connect your GitHub repository
- **GitHub Pages**: Use `npm run deploy`
- **AWS S3**: Upload the `build` folder to an S3 bucket

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🙏 Acknowledgments

- **ZenQuotes API**: For providing the quote data
- **React Team**: For the amazing framework
- **Tailwind CSS**: For the utility-first CSS framework
- **TypeScript Team**: For the type-safe JavaScript experience

---

**Built with ❤️ using React, TypeScript, and Tailwind CSS**
