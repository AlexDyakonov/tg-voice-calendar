import { Card } from "@/components/ui/card";
import { Mic, Calendar, CloudDownload } from "lucide-react";

const Features = () => {
  const features = [
    {
      icon: <Mic className="w-8 h-8 text-blue-600" />,
      title: "Понимает русский язык",
      description: "Распознаёт речь на русском языке с высокой точностью",
      emoji: "🗣️"
    },
    {
      icon: <Calendar className="w-8 h-8 text-indigo-600" />,
      title: "Создаёт .ics-файлы",
      description: "Совместимо с Google Calendar, Outlook и другими приложениями",
      emoji: "📅"
    },
    {
      icon: <CloudDownload className="w-8 h-8 text-green-600" />,
      title: "Готовые файлы",
      description: "Получайте готовые .ics файлы для добавления в календарь",
      emoji: "🔐"
    },
    {
      icon: <div className="w-8 h-8 bg-gradient-to-r from-yellow-400 to-orange-500 rounded-full flex items-center justify-center text-white font-bold">₽</div>,
      title: "Бесплатно",
      description: "Никаких скрытых платежей или ограничений",
      emoji: "🎁"
    }
  ];

  return (
    <section className="py-24 px-6 lg:px-8">
      <div className="mx-auto max-w-6xl">
        <div className="text-center mb-16">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            Почему выбирают наш бот?
          </h2>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Простое решение для тех, кто ценит своё время и удобство планирования
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          {features.map((feature, index) => (
            <Card
              key={index}
              className="p-6 text-center hover:shadow-lg transition-all duration-300 hover:scale-105 border-0 bg-white/80 backdrop-blur-sm animate-fade-in"
              style={{ animationDelay: `${index * 100}ms` }}
            >
              <div className="mb-4 flex justify-center">
                <div className="p-3 bg-gray-50 rounded-full">
                  {feature.icon}
                </div>
              </div>
              <div className="text-3xl mb-3">{feature.emoji}</div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                {feature.title}
              </h3>
              <p className="text-gray-600 text-sm leading-relaxed">
                {feature.description}
              </p>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Features;
