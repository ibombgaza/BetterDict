class CallableProperty(property):
	call = None
	def __call__(self, *args, **kwargs):
		if not CallableProperty.call:
			return self.__get__()
		if CallableProperty.call is not callable:
			return CallableProperty.call
		return CallableProperty.call(*args, **kwargs)

class Wrapper:
	slots = ('value', '_identity_hash')

	def __init__(self, value):
		self.value = value
		self._identity_hash = id(self)  # Постоянный хеш для словарей

	def __repr__(self):
		return f'>({self.value})<'

	def __hash__(self):
		# Для использования в словарях/множествах - постоянный хеш
		return self._identity_hash

	def __eq__(self, other):
		if not isinstance(other, type(self)):
			return False
		return self.value == other.value

	def content_hash(self):
		# Отдельный метод для хеша содержимого
		return hash(tuple(self.value)) if hasattr(self.value, 'iter') else hash(self.value)

	def __getitem__(self, index):
		return self.value

	def __setitem__(self, index, value):
		self.value = value

	def	__bytes__(self):
		return bytes(self.value)

def uniquely(lst):
	indices_to_remove = []
	seen_values = []
	seen_indices = []

	for index, value in enumerate(lst):
		if value in seen_values:
			# Находим индекс первого вхождения этого значения
			first_occurrence_index = seen_indices[seen_values.index(value)]
			indices_to_remove.append(first_occurrence_index)
			# Обновляем информацию о последнем вхождении
			seen_indices[seen_values.index(value)] = index
		else:
			# Добавляем новое значение и его индекс
			seen_values.append(value)
			seen_indices.append(index)

	unique_list = [v for i, v in enumerate(lst) if i not in indices_to_remove]
	sorted_indices = sorted(indices_to_remove, reverse=True)

	return unique_list, sorted_indices


def deep_contains(container, target, seen_ids=()):
	"""
	Рекурсивно проверяет, содержится ли target в container (включая вложенные структуры).
	Использует кортеж seen_ids для отслеживания посещенных объектов (по их id).
	"""
	# Проверяем, не видели ли мы уже этот контейнер (защита от циклических ссылок)
	if id(container) in seen_ids:
		return False

	# Прямое сравнение
	if container is target:
		return True

	# Добавляем текущий контейнер в seen_ids
	new_seen = seen_ids + (id(container),)

	# Для словарей проверяем и ключи, и значения
	if isinstance(container, dict):
		for key, value in container.items():
			if deep_contains(key, target, new_seen) or deep_contains(value, target, new_seen):
				return True
		return False

	# Для итерируемых объектов (кроме строк)
	if hasattr(container, '__iter__') and not isinstance(container, str):
		try:
			for item in container:
				if deep_contains(item, target, new_seen):
					return True
			return False
		except TypeError:
			# Некоторые итерируемые объекты могут требовать специальной обработки
			pass

	return False