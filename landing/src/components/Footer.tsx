
const Footer = () => {
  return (
    <footer className="py-12 px-6 lg:px-8 bg-gray-50 border-t border-gray-100">
      <div className="mx-auto max-w-4xl text-center">
        <p className="text-gray-600 mb-2">
          Создано командой <strong className="text-gray-900">Шампиньоны</strong>
        </p>
        <div className="flex justify-center items-center space-x-6 text-sm text-gray-500">
          <a 
            href="https://shamps.dev" 
            target="_blank" 
            rel="noopener noreferrer"
            className="hover:text-blue-600 transition-colors"
          >
            shamps.dev
          </a>
          <a 
            href="https://t.me/shampsdev" 
            target="_blank" 
            rel="noopener noreferrer"
            className="hover:text-blue-600 transition-colors"
          >
            t.me/shampsdev
          </a>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
