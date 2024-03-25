from .utils import full_change_macros, Cache
from celery import shared_task



@shared_task(bind=True)
def change(self, sheet):
    """
    Планирует повторную задачу с этими же параметрами

    ----
    Args:
        self: экземпляр задачи, т.е. ссылка на саму себя
        sheet: номер листа в строковом виде
    ----

    Returns:
        Записывает значение в Redis в виде пары "ключ-значения",
        где task_id - это id запланированной задачи

    """
    r = Cache()
    full_change_macros(sheet)
    next_task = self.apply_async(args=[sheet], countdown=21600)
    return r.redis.set('task_id', next_task.id)



