
import { Card } from "@/components/ui/card";
import { Mic, Brain, FileText, Calendar } from "lucide-react";

const HowItWorks = () => {
  const steps = [
    {
      number: "1",
      title: "Отправьте голосовое",
      description: "Просто запишите голосовое сообщение с планами",
      example: "«Завтра в 15:00 встреча с клиентом»",
      color: "from-blue-500 to-blue-600",
      icon: <Mic className="w-6 h-6 text-white" />
    },
    {
      number: "2", 
      title: "Бот распознаёт речь",
      description: "ИИ извлекает дату, время и описание события",
      example: "Дата: завтра, Время: 15:00, Событие: встреча с клиентом",
      color: "from-indigo-500 to-indigo-600",
      icon: <Brain className="w-6 h-6 text-white" />
    },
    {
      number: "3",
      title: "Получите .ics-файл",
      description: "Скачайте готовый файл-событие для календаря",
      example: "📎 meeting_2024-06-25.ics",
      color: "from-purple-500 to-purple-600",
      icon: <FileText className="w-6 h-6 text-white" />
    },
    {
      number: "4",
      title: "Добавьте в календарь",
      description: "Одним нажатием событие появится в вашем календаре",
      example: "Встреча автоматически добавлена!",
      color: "from-green-500 to-green-600",
      icon: <Calendar className="w-6 h-6 text-white" />
    }
  ];

  return (
    <section className="py-24 px-6 lg:px-8 bg-gray-50">
      <div className="mx-auto max-w-5xl">
        <div className="text-center mb-16">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            Как это работает?
          </h2>
          <p className="text-lg text-gray-600">
            Четыре простых шага до идеального планирования
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {steps.map((step, index) => (
            <Card
              key={index}
              className="p-6 border-0 shadow-lg hover:shadow-xl transition-all duration-300 animate-fade-in bg-white"
              style={{ animationDelay: `${index * 150}ms` }}
            >
              <div className="text-center">
                <div className={`w-16 h-16 bg-gradient-to-r ${step.color} rounded-full flex items-center justify-center mx-auto mb-4 relative`}>
                  {step.icon}
                  <div className="absolute -top-2 -right-2 w-6 h-6 bg-white rounded-full flex items-center justify-center text-xs font-bold text-gray-700">
                    {step.number}
                  </div>
                </div>
                
                <h3 className="text-lg font-semibold text-gray-900 mb-3">
                  {step.title}
                </h3>
                
                <p className="text-gray-600 text-sm mb-4 leading-relaxed">
                  {step.description}
                </p>
                
                <div className="bg-gray-100 rounded-lg p-3 text-xs text-gray-700 font-mono">
                  {step.example}
                </div>
              </div>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
};

export default HowItWorks;
