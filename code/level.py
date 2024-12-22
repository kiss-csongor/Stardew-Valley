from matplotlib.layout_engine import LayoutEngine
import pygame 
from settings import *
from player import Player
from overlay import Overlay
from sprites import *
from pytmx.util_pygame import load_pygame
from sprites import Water
from support import *

class Level:
	def __init__(self):

		# get the display surface
		self.display_surface = pygame.display.get_surface()

		# sprite groups
		self.all_sprites = CameraGroup()
		self.collision_sprites = pygame.sprite.Group()

		self.setup()
		self.overlay = Overlay(self.player)

	def setup(self):
		tmx_data = load_pygame('./data/map.tmx')

		# house
		for layer in ['HouseFloor','HouseFurnitureBottom']:
			for x, y, surf in tmx_data.get_layer_by_name(layer).tiles():
				Generic((x * TILE_SIZE, y * TILE_SIZE), surf, self.all_sprites, LAYERS['house bottom'])

		for layer in ['HouseWalls','HouseFurnitureTop']:
			for x, y, surf in tmx_data.get_layer_by_name(layer).tiles():
				Generic((x * TILE_SIZE, y * TILE_SIZE), surf, self.all_sprites)

		# fence
		for x, y, surf in tmx_data.get_layer_by_name('Fence').tiles():
			Generic((x * TILE_SIZE, y * TILE_SIZE), surf, [self.all_sprites, self.collision_sprites])

		# water
		water_frames = import_folder('./graphics/water')
		for x, y, surf in tmx_data.get_layer_by_name('Water').tiles():
			Water((x * TILE_SIZE, y * TILE_SIZE), water_frames, self.all_sprites, LAYERS['water'])

		# wild flowers
		for obj in tmx_data.get_layer_by_name('Decoration'):
			WildFlower((obj.x, obj.y), obj.image, [self.all_sprites, self.collision_sprites])

		# Trees
		for obj in tmx_data.get_layer_by_name('Trees'):
			Tree((obj.x, obj.y), obj.image, [self.all_sprites, self.collision_sprites], obj.name)
				
		# collision tiles
		for x, y, surf in tmx_data.get_layer_by_name('Collision').tiles():
			Generic((x * TILE_SIZE, y * TILE_SIZE), pygame.Surface((TILE_SIZE, TILE_SIZE)), self.collision_sprites)

		# Player
		for obj in tmx_data.get_layer_by_name('Player'):
			if obj.name == 'Start':
				self.player = Player((obj.x,obj.y), self.all_sprites, self.collision_sprites)

		Generic(pos = (0,0),
		  		surf = pygame.image.load('./graphics/world/ground.png').convert_alpha(),
				groups = self.all_sprites, 
				z = LAYERS['ground'])
		

	def run(self,dt):
		self.display_surface.fill('green')
		self.all_sprites.custom_draw(self.player)
		self.all_sprites.update(dt)

		self.overlay.display()

class CameraGroup(pygame.sprite.Group):
	def __init__(self):
		super().__init__()
		self.display_surface = pygame.display.get_surface()
		self.offset = pygame.math.Vector2()
		self.half_w = self.display_surface.get_size()[0] // 2
		self.half_h = self.display_surface.get_size()[1] // 2
		self.camera_type = 'center_camera'

		# box setup
		self.camera_borders = {'left': 200, 'right': 200, 'top': 100, 'bottom': 100}
		l = self.camera_borders['left']
		t = self.camera_borders['top']
		w = self.display_surface.get_size()[0] - (self.camera_borders['left'] + self.camera_borders['right'])
		h = self.display_surface.get_size()[1] - (self.camera_borders['top'] + self.camera_borders['bottom'])
		self.camera_rect = pygame.Rect(l,t,w,h)

	def camera_center(self, target):
		self.offset.x = target.rect.centerx - SCREEN_WIDTH / 2
		self.offset.y = target.rect.centery - SCREEN_HEIGHT / 2

	def box_target_camera(self, target):

		if target.rect.right > self.camera_rect.right:
			self.camera_rect.right = target.rect.right
		if target.rect.left < self.camera_rect.left:
			self.camera_rect.left = target.rect.left
		if target.rect.top < self.camera_rect.top:
			self.camera_rect.top = target.rect.top
		if target.rect.bottom > self.camera_rect.bottom:
			self.camera_rect.bottom = target.rect.bottom

		self.offset.x = self.camera_rect.left - self.camera_borders['left']
		self.offset.y = self.camera_rect.top - self.camera_borders['top']

	def custom_draw(self, player):
		keys = pygame.key.get_pressed()

        # Toggle camera type with CAPSLOCK
		if keys[pygame.K_CAPSLOCK]:
			if self.camera_type == 'box_target_camera':
				self.camera_type = 'center_camera'
			else:
				self.camera_type = 'box_target_camera'

        # Apply appropriate camera logic
		if self.camera_type == 'box_target_camera':
			self.box_target_camera(player)
		if self.camera_type == 'center_camera':
			self.camera_center(player)


		for layer in LAYERS.values():
			for sprite in sorted(self.sprites(), key = lambda sprite: sprite.rect.centery):
				if sprite.z == layer:
					offset_rect = sprite.rect.copy()
					offset_rect.center -= self.offset
					self.display_surface.blit(sprite.image, offset_rect)

		# pygame.draw.rect(self.display_surface, 'yellow', self.camera_rect, 5)	