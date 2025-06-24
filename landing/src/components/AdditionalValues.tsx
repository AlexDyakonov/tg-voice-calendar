
import { Card } from "@/components/ui/card";
import { Clock, Mic, Calendar, Shield, Settings } from "lucide-react";

const AdditionalValues = () => {
  const values = [
    {
      icon: <Clock className="w-8 h-8 text-blue-600" />,
      title: "Экономит время",
      description: "Не нужно печатать вручную — просто говорите"
    },
    {
      icon: <Mic className="w-8 h-8 text-green-600" />,
      title: "Говорите, как удобно",
      description: "Бот понимает естественную речь и любые формулировки"
    },
    {
      icon: <Calendar className="w-8 h-8 text-purple-600" />,
      title: "Никогда не забудете",
      description: "Все важные встречи автоматически попадают в календарь"
    },
    {
      icon: <Shield className="w-8 h-8 text-indigo-600" />,
      title: "Безопасно",
      description: "Работает офлайн, ваши данные не уходят в облако"
    },
    {
      icon: <Settings className="w-8 h-8 text-orange-600" />,
      title: "Для повседневного использования",
      description: "Личные дела, встречи, напоминания — всё в одном месте"
    }
  ];

  return (
    <section className="py-24 px-6 lg:px-8">
      <div className="mx-auto max-w-6xl">
        <div className="text-center mb-16">
          <div className="text-4xl mb-4">🏆</div>
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            Дополнительные преимущества
          </h2>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Всё, что делает голосовое планирование по-настоящему удобным
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {values.map((value, index) => (
            <Card
              key={index}
              className="p-6 hover:shadow-lg transition-all duration-300 hover:scale-105 border-0 bg-white/80 backdrop-blur-sm animate-fade-in"
              style={{ animationDelay: `${index * 120}ms` }}
            >
              <div className="text-center">
                <div className="mb-4 flex justify-center">
                  <div className="p-3 bg-gray-50 rounded-full">
                    {value.icon}
                  </div>
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-3">
                  {value.title}
                </h3>
                <p className="text-gray-600 text-sm leading-relaxed">
                  {value.description}
                </p>
              </div>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
};

export default AdditionalValues;
