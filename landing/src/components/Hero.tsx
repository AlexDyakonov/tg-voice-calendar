
import { Button } from "@/components/ui/button";
import { Mic, Calendar, MessageCircle } from "lucide-react";

const Hero = () => {
  const handleTelegramClick = () => {
    window.open("https://t.me/caldev_voice_bot", "_blank");
  };

  return (
    <section className="relative overflow-hidden px-6 py-24 lg:px-8">
      <div className="mx-auto max-w-4xl text-center">
        {/* Floating icons animation */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute top-20 left-1/4 animate-pulse">
            <Mic className="w-8 h-8 text-blue-300 opacity-60" />
          </div>
          <div className="absolute top-32 right-1/4 animate-pulse delay-1000">
            <Calendar className="w-6 h-6 text-indigo-300 opacity-60" />
          </div>
          <div className="absolute bottom-32 left-1/3 animate-pulse delay-500">
            <MessageCircle className="w-7 h-7 text-purple-300 opacity-60" />
          </div>
        </div>

        <div className="relative">
          {/* Main heading */}
          <h1 className="text-5xl font-bold tracking-tight text-gray-900 sm:text-7xl mb-6 animate-fade-in">
            Говори — и планируй
          </h1>
          
          {/* Subheading */}
          <p className="text-xl leading-8 text-gray-600 mb-8 max-w-2xl mx-auto animate-fade-in delay-200">
            Телеграм-бот, который превращает голос в событие календаря
          </p>

          {/* Visual element */}
          <div className="flex justify-center items-center mb-12 animate-scale-in delay-300">
            <div className="relative">
              <div className="bg-gradient-to-r from-blue-500 to-indigo-600 rounded-full p-6 shadow-2xl">
                <Mic className="w-12 h-12 text-white" />
              </div>
              <div className="absolute -top-2 -right-2 bg-green-500 rounded-full p-2 animate-pulse">
                <div className="w-3 h-3 bg-white rounded-full"></div>
              </div>
            </div>
            <div className="mx-8 text-gray-400">
              <div className="flex space-x-1">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-pulse"></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-pulse delay-100"></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-pulse delay-200"></div>
              </div>
            </div>
            <div className="bg-white rounded-xl p-4 shadow-lg border">
              <Calendar className="w-8 h-8 text-indigo-600" />
            </div>
          </div>

          {/* CTA Button */}
          <Button
            onClick={handleTelegramClick}
            size="lg"
            className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white px-8 py-4 text-lg font-semibold rounded-full shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105 animate-fade-in delay-500"
          >
            Открыть в Telegram
          </Button>

          <p className="mt-4 text-sm text-gray-500 animate-fade-in delay-700">
            Попробуйте прямо сейчас — это бесплатно
          </p>
        </div>
      </div>
    </section>
  );
};

export default Hero;
