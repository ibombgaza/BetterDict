from copy import copy, deepcopy
from .utils import *

class BetterDict:
	"""This one is better"""
	slots = ('__keys', '__values', '__mutability')
	show_as_str = []
	check_mutability_for_eq = True
	raise_errors_if_immut = True
	
	def __new__(cls, keys=(), values=(), mutability=True, **dictionary):
		if not (keys or values or dictionary or mutability):
			return empty_immut
		return object.__new__(cls)

	def __init__(self, keys=(), values=(), mutability=True, **dictionary):
		"""Initialization of an object"""
		# Iterability check
		# Проверка итерабельности
			
		if self is empty_immut:
			return
		if not keys and not values and mutability and not dictionary:
			self.__keys = []
			self.__values = []
			return
		if not hasattr(keys, '__iter__') or not hasattr(values, '__iter__'):
			raise TypeError('Keys or Values are not iterable')

		# Prohibition of some types
		# Запрет некоторых типов
		if isinstance(keys, (set, frozenset)) or isinstance(values, (set, frozenset)):
			raise TypeError('sets and frozensets are not stable')
		for key, val in zip(keys, values):
			if isinstance(key, slice):
				raise TypeError(f"'{slice.__name__}' can't be used as key")
			if key == '[...]' or val == '[...]':
				raise ValueError("string '[...]' can't be used in key or value, it's for recursive dictionaries")

		self.__keys = []
		self.__values = []

		# Case 1: keys is dict
		# Случай 1: keys - словарь
		if isinstance(keys, dict):
			self.__keys.extend(keys.keys())
			self.__values.extend(keys.values())

			# If values is a dict too - adds its elements
			# Если values тоже словарь - добавляем его значения
			if isinstance(values, dict):
				self.__keys.extend(values.keys())
				self.__values.extend(values.values())
			elif values:
				# if values isnt a dict and not empty
				# values не словарь и не пустой
				raise ValueError('Keys and values length mismatch')
		else:
			# keys не словарь
			self.__keys.extend(keys)

			# Обработка values
			if isinstance(values, dict):
				raise ValueError('Keys and values length mismatch')
			else:
				self.__values.extend(values)

		# Добавление keyword-аргументов
		if dictionary:
			self.__keys.extend(dictionary.keys())
			self.__values.extend(dictionary.values())

		# Проверка соответствия размеров
		if len(self.__keys) != len(self.__values):
			raise ValueError('Keys and values length mismatch')

		# Удаление дубликатов ключей
		if self.__keys:
			self.__keys, removed_indices = uniquely(self.__keys)
			for i in sorted(removed_indices, reverse=True):
				del self.__values[i]

		# Фиксация состояния
		self.__mutability = bool(mutability)
		if not self.__mutability:
			self.__keys = tuple(self.__keys)
			self.__values = tuple(self.__values)

	@classmethod
	def fromkeys(cls, keys, default=None):
		"""Makes a dictionary without unique values

		Создаёт словарь без уникальных значений"""
		return cls(keys, (default,)*len(keys))

	# Строки 56-61: Property для доступа к атрибутам

	def __iter__(self):
		"""zip object for iterarion

		zip объект для итерации"""
		return zip(self.__keys, self.__values)

	@property
	def keys(self):
		"""shallowcopy of keys

		поверхностная копия ключей"""
		if isinstance(self.__keys, list):
			return copy(self.__keys)
		return self.__keys

	@property
	def values(self):
		"""shallowcopy of values

		поверхностная копия значений"""
		if isinstance(self.__values, list):
			return copy(self.__values)
		return self.__values

	@property
	def mutability(self):
		"""get mutability status of dictionary

		возвращает изменяемость словаря"""
		return self.__mutability

	@CallableProperty
	def shallowcopy(self):
		"""Makes new object and attributes, but they include links to same objects

		Создаёт новый объект и атрибуты, но они включают одинаковые ссылки"""
		return copy(self)

	@CallableProperty
	def deepcopy(self):
		"""Recursively copies everything from dictionary

		Рекурсивно копирует всё из словаря"""
		return deepcopy(self)

	@CallableProperty
	def pairs(self):
		"""returns zip object for iterating

		возвращает zip объект для итерации"""
		return zip(self.__keys, self.__values)

	def mutable_copy(self):
		"""Return mutable copy

		Возвращает изменяемую копию"""
		if self.__mutability:
			return self
		new = object.__new__(BetterDict)
		new.__keys = list(self.__keys)
		new.__values = list(self.__values)
		new.__mutability = True
		return new

	def immutable_copy(self):
		"""Returns immutable copy

		Возвращает неизменяемую копию"""
		if self.__mutability:
			return self
		new = object.__new__(BetterDict)
		new.__keys = tuple(self.__keys)
		new.__values = tuple(self.__values)
		new.__mutability = False
		return new

	def froze(self):
		"""Say red or blue.
		Makes dictionary immutable

		Делает словарь неизменяемым"""
		if not self.__mutability:
			return
		self.__keys = tuple(self.__keys)
		self.__values = tuple(self.__values)
		self.__mutability = False

	# Строки 63-72: Методы доступа к элементам
	def __getitem__(self, key):
		"""print(MyLovelyDict[key_or_slice])
		WARNING! Use slice(0,n) instead of slice(None,n)

		ПРЕДУПРЕЖДАЮ! Используйте slice(0,n) вместо slice(None,n)"""
		if isinstance(key, slice):
			if not key.start and key.stop:
				key = slice(key.stop, key.stop+1, key.step)
			return self.__values[key]
		for i, k in enumerate(self.__keys):
			if k == key: return self.__values[i]
		raise KeyError(f'{key} doesnt exist in {self}')

	def safeget(self, key, default=None):
		"""returns an element from dict without exception
		if element doesn't exist returns default

		возвращает эелемент без исключения
		если элемента нету вернёт default"""
		try:
			return self[key]
		except KeyError:
			return default

	get = safeget

	# Строки 74-83: Методы изменения словаря
	def __setitem__(self, key, value):
		"""MyLovelyDict[key_or_slice] = MyLovelyValue"""
		if self is empty_immut or not self.__mutability:
			raise TypeError(f'{self} is immutable')
		if key == '[...]' or value == '[...]':
			raise ValueError("string '[...]' can't be used in key or value, it's for recursive dictionaries, use [Ellipsis] or Wrapper")

		# Handling slice
		# Обработка срезов
		if isinstance(key, slice):
			if not hasattr(value, 'iter'):
				raise TypeError(f"'{type(value).name}' object is not iterable")

			selected_indices = len(self.__keys)[key]
			if selected_indices != len(value):
				raise ValueError(
					f"attempt to assign sequence of size {len(value)} "
					f"to extended slice of size {len(selected_indices)}"
				)

			for i, val in zip(selected_indices, value):
				self.__values[i] = val
			return

		# ASSignment by key
		# Присваивание по ключу
		for num, k in enumerate(self.__keys):
			if k == key:
				self.__values[num] = value
				break
		else:
			self.__keys.append(key)
			self.__values.append(value)
		# I just love for-else

	def keys_with(self, value):
		"""Returns all keys with given value

		Возвращает все ключи с переданным значением"""
		if not self.__values:
			return ()
		return (*[k for i, k in enumerate(self.__keys) if self.__values[i] == value],)

	def pop(self, key, exc_or_default=KeyError):
		"""Deletes item and returns it

		Удаляет элемент и возвращает его"""
		try:
			if isinstance(key, slice):
				return self.__keys[key], self.__values[key]
			for i, val in enumerate(self.__values):
				self_key = self[key]
				if self_key == val:
					key = slice(i,i+1)
					return self_key
			else:
				if not isinstance(exc_or_default, BaseException):
					return exc_or_default
				raise exc_or_default
		finally:
			del self.__keys[key], self.__values[key]

	def __delitem__(self, key):
		"""del MyLovelyDict[MyNotLovelyElement]"""
		self.pop(key)

	# Строки 85-95: Служебные методы
	def __sizeof__(self):
		"""size of object in bytes

		количество занимаемой памяти в байтах"""
		if self is empty_immut:
			return 32
		return self.__keys.__sizeof__() + self.__values.__sizeof__() + \
		self.__mutability.__sizeof__() + object.__sizeof__(self)

	def __repr__(self):
		"""Converting to string with precise recursive detection

		Конвертация в строку с какими-то там обнаружениями рекурсии, понятия не имею как это работает"""
		if self is _recursive_link:
			return '[...]'
		if self is empty_immut:
			return 'EmptyImmutableBetterDict'
		if not self.__keys:
			return 'EmptyMutableBetterDict'
		items = []
		AsStr = tuple(type(self).show_as_str)

		def process_value(v, seen_ids=()):
			# Защита от циклических ссылок
			if id(v) in seen_ids:
				return _recursive_link

			new_seen = seen_ids + (id(v),)

			# Проверяем рекурсивные ссылки
			if v is self or deep_contains(v, self, new_seen):
				return _recursive_link

			# Обрабатываем вложенные структуры
			if isinstance(v, (list, tuple, set, frozenset)) and not isinstance(v, str):
				if isinstance(v, tuple):
					return tuple(process_value(item, new_seen) for item in v)
				if isinstance(v, list):
					return [process_value(item, new_seen) for item in v]
				if isinstance(v, set):
					return {process_value(item, new_seen) for item in v}
				if isinstance(v, frozenset):
					return frozenset(process_value(item, new_seen) for item in v)

			return repr(v) if not v in AsStr else v

		for key, val in zip(self.__keys, self.__values):
			key_str = process_value(key, (id(self),))
			val_str = process_value(val, (id(self),))
			items.append(f'{key_str}: {val_str}')

		if self.__mutability:
			return '[' + '; '.join(items) + ']'
		return '(' + '; '.join(items) + ')'

	def info(self, ret_type=str):
		"""Nerd representation for devs

		Душная репрезентация для разрабов"""
		keys, values = ('size', 'id', 'keys', 'values', 'length'),	(self.__sizeof__(), id(self), self.__keys, self.__values, len(self.__keys))

		if ret_type == str:
			return f'size = {self.__sizeof__()} bytes, id = {id(self)}, keys = {self.__keys}, values = {self.__values}, len = {len(self.__keys)}'
		if ret_type in (list, tuple, set, frozenset):
			ret_type(values)
		if ret_type is dict:
			return dict(zip(keys,values))
		if ret_type is BetterDict:
			tmp = object.__new__(BetterDict)
			tmp.__keys, tmp.__values, tmp.__mutability = keys, values, False
			return tmp
		if ret_type is zip:
			return zip(keys, values)
		raise TypeError(f"I dont know how to work with {ret_type} in info method")

	def __len__(self):
		"""amount of elements in dictionary

		количество элементов словаря"""
		return len(self.__keys)

	# Строки 97-102: Дополнительные методы
	def to_object(self, obj, names=None):
		"""Adds attributes to an object from BetterDict

		Добавляет атрибуты к объекту из словаря"""
		if not self.__values:
			return obj
		if names is None:
			names = BetterDict(self.__keys, self.__keys)
		for key, realkey in zip(names.__keys, names.__values):
			setattr(obj, str(key), self.__values[realkey])
		return obj

	def shrink(self):
		"""Deletes list overallocation,
		no-op if dictionary is immutable

		Удаляет избыточную информацию списков,
		ничего не делает для неизменяемых словарей"""
		if not self.__mutability:
			return
		self.__keys = list(self.__keys)
		self.__values = list(self.__values)

	def __eq__(self, other):
		"""self == other checking"""
		if other.__class__ != self.__class__:
			return False
		return self.__keys == other.__keys \
			and self.__values == other.__values \
			and (self.__mutability == other.__mutability or not BetterDict.check_mutability_for_eq)

	def __bool__(self):
		"""Returns False if dictionary is empty, else True

		Возвращает False если словарь пуст, иначе вернёт True"""
		return bool(self.__values.__len__())

	def __contains__(self, key):
		"""Checks that given key exist

		Проверяет существование ключа"""
		return key in self.__keys

	def in_values(self, value):
		"""Checks that given value is in dictionaries values

		Проверяет есть ли переданное значение в списке значений словаря"""
		return value in self.__values

	def __add__(self, other):
		"""Unite 2 dictionaries with first + second

		Объединить 2 словаря с помощью сложения"""
		if self is empty_immut or (not self.__keys and not self.__values):
			return other
		if not isinstance(other, BetterDict):
			raise TypeError(f"Adding {str(type(other)).replace('<class ', '')[:-1]} to BetterDict")
		new_keys = self.__keys
		new_values = self.__values
		new_keys.extend(other.__keys)
		new_values.extend(other.__values)
		return BetterDict(new_keys, new_values)

	# noinspection PyTypeChecker
	def __iadd__(self, other):
		"""Extend dictionary with another using +=

		Объединить 2 словаря с помощью +="""
		#Как я такое говно написал, там хуже было, сейчас исправляю
		if self is empty_immut or not self.__keys:
			return other
		if not isinstance(other, (BetterDict, tuple, list, zip)):
			raise TypeError(f"Adding {str(type(other)).replace('<class ', '')[:-1]} to BetterDict")

		if isinstance(other, zip):
			if len(tuple(other)[0]) != 2:
				raise ValueError("Pairs expected")
			other = tuple(zip(*other))

		elif isinstance(other, (tuple, list)):
			if len(other) != 2:
				raise ValueError("Pairs expected")
			self.extend(other[0], other[1])

		elif isinstance(other, BetterDict):
			self.__keys.extend(other.__keys)
			self.__values.extend(other.__values) #ранее было только 2 extend! Ужас
			self.__init__(self.__keys, self.__values, self.__mutability)
		return self

	def extend(self, keys, values):
		"""Extends dictionary with 2 lists of keys and values, to unite 2 dictionaries use __add__
		Not finished yet

		Расширяет словарь 2 списками для ключей и значений, для объеденения 2 словарей используй __add__
		Не закончено, в целом думаю работает"""

		new = BetterDict.fast_init([*self.__keys,*keys], [*self.__values, *values])
		if self._raise_if_immut():
			return new
		self.__keys, self.__values = new.__keys, new.__values
		return self

	def to_dict(self, convert_nonhashable=Wrapper):
		"""Converts to dict

		Конвертирует в dict"""
		new_dict = {}
		for key, val in self.pairs:
			try:
				hash(key)
			except TypeError:
				key = convert_nonhashable(key)
			new_dict[key] = val
		return new_dict

	def clear(self):
		if BetterDict._raise_if_immut(self):
			return empty_immut
		self.__keys, self.__values = [],[]
		return self

	@classmethod
	def fast_init(cls, keys, values, mutability=True):
		if not (keys or values or mutability):
			return empty_immut
		new = object.__new__(BetterDict)
		new.__keys, new.__values, new.__mutability = keys, values, mutability
		return new

	@property
	def __dict__(self):
		"""I dont recommend this

		Не советую это говно"""
		return self.__class__.fast_init(['__keys', '__values', '__mutability'], [self.__keys, self.__values, self.__mutability], mutability=False)

	def _raise_if_immut(self):
		"""Raise TypeError if self is immutable

		Поднять TypeError если объект неизменяемый"""
		if not self.__mutability:
			if self.__class__.raise_errors_if_immut:
				raise TypeError(f"{self} is immutable")
			return True
		return False

	def swap_all(self):
		"""Swaps keys and values

		Меняет местами ключи и значения"""
		if self._raise_if_immut():
			return BetterDict.fast_init(self.__values, self.__keys, mutability=False)
		self.__keys, self.__values = self.__values, self.__keys
		return self

	def swap_at(self, index):
		"""Swaps key and value on index

		Меняет местами ключи и значения"""
		if self._raise_if_immut():
			new = BetterDict.fast_init(self.__keys, self.__values)
			return new.swap_at(index)
		if isinstance(index, slice) and index.start is None and not index.step:
			index = index.stop

		if not isinstance(index, (int, slice)):
			raise TypeError("Index isnt a slice or int")
		self.__keys[index], self.__values[index] = self.__values[index], self.__keys[index]
		return self

	def __reversed__(self):
		"""Returns reversed copy

		Возвращает реверсированную копию"""
		return BetterDict.fast_init(reversed(self.__keys), reversed(self.__values), self.__mutability)

	def reverse(self):
		"""Reverses the order

		Реверсирует порядок"""
		if self._raise_if_immut():
			return reversed(self)
		self.__keys.reverse()
		self.__values.reverse()
		return self

	def setdefault(self, key, default=None):
		"""Gets value from dictionary,
		if doesn't exist sets to default and returns

		Возвращает значение из словаря, если ключа не существует,
		то устанавливает default значение и возвращает его"""
		if not self.__mutability:
			raise TypeError(f"{self} is immutable, don't use setdefault for it")

		if key not in self:
			self[key] = default
			return default
		return self[key]

_recursive_link = object.__new__(BetterDict)

empty_immut = object.__new__(BetterDict)

empty_immut._BetterDict__keys, empty_immut._BetterDict__values,empty_immut._BetterDict__mutability = (),(),False