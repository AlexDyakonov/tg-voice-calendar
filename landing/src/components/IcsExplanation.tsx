
import { Card } from "@/components/ui/card";
import { Calendar, Smartphone, Monitor } from "lucide-react";

const IcsExplanation = () => {
  const platforms = [
    {
      icon: <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-blue-600 rounded-full flex items-center justify-center text-white font-bold text-sm">G</div>,
      name: "Google Calendar"
    },
    {
      icon: <div className="w-8 h-8 bg-gradient-to-r from-gray-600 to-gray-700 rounded-full flex items-center justify-center text-white font-bold text-sm">O</div>,
      name: "Outlook"
    },
    {
      icon: <Smartphone className="w-8 h-8 text-gray-600" />,
      name: "Apple Calendar"
    },
    {
      icon: <Monitor className="w-8 h-8 text-indigo-600" />,
      name: "Другие календари"
    }
  ];

  return (
    <section className="py-16 px-6 lg:px-8 bg-gradient-to-br from-indigo-50 to-blue-50">
      <div className="mx-auto max-w-4xl">
        <Card className="p-8 border-0 shadow-lg bg-white/80 backdrop-blur-sm">
          <div className="text-center mb-8">
            <div className="flex justify-center mb-4">
              <div className="p-3 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-full">
                <Calendar className="w-8 h-8 text-white" />
              </div>
            </div>
            <h3 className="text-2xl font-bold text-gray-900 mb-4">
              Что такое .ics файл?
            </h3>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              .ics — это универсальный формат события, который открывается в любом календаре. 
              Просто нажмите на файл и добавьте встречу одним нажатием.
            </p>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            {platforms.map((platform, index) => (
              <div
                key={index}
                className="text-center p-4 rounded-lg hover:bg-gray-50 transition-colors duration-200"
              >
                <div className="flex justify-center mb-3">
                  {platform.icon}
                </div>
                <p className="text-sm font-medium text-gray-700">
                  {platform.name}
                </p>
              </div>
            ))}
          </div>

          <div className="mt-8 text-center">
            <p className="text-gray-600 italic">
              ✨ Никаких настроек — просто откройте файл и всё готово!
            </p>
          </div>
        </Card>
      </div>
    </section>
  );
};

export default IcsExplanation;
