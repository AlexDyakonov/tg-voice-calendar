
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

const CTA = () => {
  const handleTryClick = () => {
    window.open("https://t.me/caldev_voice_bot", "_blank");
  };

  return (
    <section className="py-24 px-6 lg:px-8">
      <div className="mx-auto max-w-4xl">
        <Card className="bg-gradient-to-r from-blue-600 to-indigo-700 border-0 p-12 text-center text-white shadow-2xl">
          <h2 className="text-3xl font-bold mb-4">
            Готовы упростить планирование?
          </h2>
          <p className="text-xl opacity-90 mb-8 max-w-2xl mx-auto">
            Присоединяйтесь к тысячам пользователей, которые уже планируют голосом
          </p>

          <div className="flex justify-center">
            <Button
              onClick={handleTryClick}
              size="lg"
              variant="secondary"
              className="px-8 py-4 text-lg font-semibold bg-white text-blue-600 hover:bg-gray-100 rounded-full shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105"
            >
              Попробовать
            </Button>
          </div>

          <div className="mt-8 text-sm opacity-75">
            <p>✨ Начните использовать прямо сейчас — регистрация не требуется</p>
            <p className="mt-2 font-mono text-blue-200">@caldev_voice_bot</p>
          </div>
        </Card>

        {/* Trust indicators */}
        <div className="mt-12 text-center">
          <p className="text-gray-500 text-sm mb-4">Безопасно и надёжно</p>
          <div className="flex justify-center items-center space-x-8 text-gray-400">
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-green-500 rounded-full"></div>
              <span className="text-sm">Приватность данных</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
              <span className="text-sm">Без регистрации</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-purple-500 rounded-full"></div>
              <span className="text-sm">Мгновенный результат</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default CTA;
