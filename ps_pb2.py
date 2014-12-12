# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: ps.proto

from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)




DESCRIPTOR = _descriptor.FileDescriptor(
  name='ps.proto',
  package='planetarysettlement',
  serialized_pb='\n\x08ps.proto\x12\x13planetarysettlement\"\xc4\x01\n\tGameState\x12\x1a\n\x12upgrades_available\x18\x01 \x03(\x08\x12.\n\x0bstack_tiles\x18\x02 \x03(\x0b\x32\x19.planetarysettlement.Tile\x12.\n\x0btable_tiles\x18\x03 \x03(\x0b\x32\x19.planetarysettlement.Tile\x12\r\n\x02id\x18\x04 \x02(\r:\x01\x31\x12,\n\x07players\x18\x05 \x03(\x0b\x32\x1b.planetarysettlement.Player\"\xe1\x02\n\x04Tile\x12\x14\n\ttile_type\x18\x01 \x02(\r:\x01\x31\x12\x1b\n\x10tile_orientation\x18\x02 \x01(\r:\x01\x31\x12\x19\n\rupgrade_built\x18\x03 \x01(\x11:\x02-1\x12\x18\n\rupgrade_owner\x18\x04 \x01(\r:\x01\x30\x12\x16\n\x0b\x65lectricity\x18\x05 \x01(\r:\x01\x30\x12\x16\n\x0binformation\x18\x06 \x01(\r:\x01\x30\x12\x10\n\x05metal\x18\x07 \x01(\r:\x01\x30\x12\x15\n\nrare_metal\x18\x08 \x01(\r:\x01\x30\x12\x10\n\x05water\x18\t \x01(\r:\x01\x30\x12\x15\n\rtile_position\x18\n \x01(\r\x12\x1e\n\x16player_1_worker_placed\x18\x0b \x01(\x08\x12\x1e\n\x16player_2_worker_placed\x18\x0c \x01(\x08\x12\x1a\n\x12\x63ity_online_status\x18\r \x01(\r\x12\x13\n\x08\x63ounters\x18\x0e \x01(\r:\x01\x30\"\xf9\x01\n\x06Player\x12\r\n\x02vp\x18\x01 \x01(\r:\x01\x30\x12\x16\n\x0b\x65lectricity\x18\x02 \x01(\r:\x01\x30\x12\x16\n\x0binformation\x18\x03 \x01(\r:\x01\x30\x12\x10\n\x05metal\x18\x04 \x01(\r:\x01\x30\x12\x15\n\nrare_metal\x18\x05 \x01(\r:\x01\x30\x12\x10\n\x05water\x18\x06 \x01(\r:\x01\x30\x12\x1d\n\x0fis_first_player\x18\x07 \x02(\x08:\x04true\x12\x1e\n\x10is_turn_to_place\x18\x08 \x02(\x08:\x04true\x12\x1c\n\x11workers_remaining\x18\t \x02(\r:\x01\x32\x12\x18\n\rtotal_workers\x18\n \x02(\r:\x01\x32')




_GAMESTATE = _descriptor.Descriptor(
  name='GameState',
  full_name='planetarysettlement.GameState',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='upgrades_available', full_name='planetarysettlement.GameState.upgrades_available', index=0,
      number=1, type=8, cpp_type=7, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='stack_tiles', full_name='planetarysettlement.GameState.stack_tiles', index=1,
      number=2, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='table_tiles', full_name='planetarysettlement.GameState.table_tiles', index=2,
      number=3, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='id', full_name='planetarysettlement.GameState.id', index=3,
      number=4, type=13, cpp_type=3, label=2,
      has_default_value=True, default_value=1,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='players', full_name='planetarysettlement.GameState.players', index=4,
      number=5, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=34,
  serialized_end=230,
)


_TILE = _descriptor.Descriptor(
  name='Tile',
  full_name='planetarysettlement.Tile',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='tile_type', full_name='planetarysettlement.Tile.tile_type', index=0,
      number=1, type=13, cpp_type=3, label=2,
      has_default_value=True, default_value=1,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='tile_orientation', full_name='planetarysettlement.Tile.tile_orientation', index=1,
      number=2, type=13, cpp_type=3, label=1,
      has_default_value=True, default_value=1,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='upgrade_built', full_name='planetarysettlement.Tile.upgrade_built', index=2,
      number=3, type=17, cpp_type=1, label=1,
      has_default_value=True, default_value=-1,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='upgrade_owner', full_name='planetarysettlement.Tile.upgrade_owner', index=3,
      number=4, type=13, cpp_type=3, label=1,
      has_default_value=True, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='electricity', full_name='planetarysettlement.Tile.electricity', index=4,
      number=5, type=13, cpp_type=3, label=1,
      has_default_value=True, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='information', full_name='planetarysettlement.Tile.information', index=5,
      number=6, type=13, cpp_type=3, label=1,
      has_default_value=True, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='metal', full_name='planetarysettlement.Tile.metal', index=6,
      number=7, type=13, cpp_type=3, label=1,
      has_default_value=True, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='rare_metal', full_name='planetarysettlement.Tile.rare_metal', index=7,
      number=8, type=13, cpp_type=3, label=1,
      has_default_value=True, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='water', full_name='planetarysettlement.Tile.water', index=8,
      number=9, type=13, cpp_type=3, label=1,
      has_default_value=True, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='tile_position', full_name='planetarysettlement.Tile.tile_position', index=9,
      number=10, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='player_1_worker_placed', full_name='planetarysettlement.Tile.player_1_worker_placed', index=10,
      number=11, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='player_2_worker_placed', full_name='planetarysettlement.Tile.player_2_worker_placed', index=11,
      number=12, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='city_online_status', full_name='planetarysettlement.Tile.city_online_status', index=12,
      number=13, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='counters', full_name='planetarysettlement.Tile.counters', index=13,
      number=14, type=13, cpp_type=3, label=1,
      has_default_value=True, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=233,
  serialized_end=586,
)


_PLAYER = _descriptor.Descriptor(
  name='Player',
  full_name='planetarysettlement.Player',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='vp', full_name='planetarysettlement.Player.vp', index=0,
      number=1, type=13, cpp_type=3, label=1,
      has_default_value=True, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='electricity', full_name='planetarysettlement.Player.electricity', index=1,
      number=2, type=13, cpp_type=3, label=1,
      has_default_value=True, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='information', full_name='planetarysettlement.Player.information', index=2,
      number=3, type=13, cpp_type=3, label=1,
      has_default_value=True, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='metal', full_name='planetarysettlement.Player.metal', index=3,
      number=4, type=13, cpp_type=3, label=1,
      has_default_value=True, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='rare_metal', full_name='planetarysettlement.Player.rare_metal', index=4,
      number=5, type=13, cpp_type=3, label=1,
      has_default_value=True, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='water', full_name='planetarysettlement.Player.water', index=5,
      number=6, type=13, cpp_type=3, label=1,
      has_default_value=True, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='is_first_player', full_name='planetarysettlement.Player.is_first_player', index=6,
      number=7, type=8, cpp_type=7, label=2,
      has_default_value=True, default_value=True,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='is_turn_to_place', full_name='planetarysettlement.Player.is_turn_to_place', index=7,
      number=8, type=8, cpp_type=7, label=2,
      has_default_value=True, default_value=True,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='workers_remaining', full_name='planetarysettlement.Player.workers_remaining', index=8,
      number=9, type=13, cpp_type=3, label=2,
      has_default_value=True, default_value=2,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='total_workers', full_name='planetarysettlement.Player.total_workers', index=9,
      number=10, type=13, cpp_type=3, label=2,
      has_default_value=True, default_value=2,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=589,
  serialized_end=838,
)

_GAMESTATE.fields_by_name['stack_tiles'].message_type = _TILE
_GAMESTATE.fields_by_name['table_tiles'].message_type = _TILE
_GAMESTATE.fields_by_name['players'].message_type = _PLAYER
DESCRIPTOR.message_types_by_name['GameState'] = _GAMESTATE
DESCRIPTOR.message_types_by_name['Tile'] = _TILE
DESCRIPTOR.message_types_by_name['Player'] = _PLAYER

class GameState(_message.Message):
  __metaclass__ = _reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _GAMESTATE

  # @@protoc_insertion_point(class_scope:planetarysettlement.GameState)

class Tile(_message.Message):
  __metaclass__ = _reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _TILE

  # @@protoc_insertion_point(class_scope:planetarysettlement.Tile)

class Player(_message.Message):
  __metaclass__ = _reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _PLAYER

  # @@protoc_insertion_point(class_scope:planetarysettlement.Player)


# @@protoc_insertion_point(module_scope)
