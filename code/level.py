from matplotlib.layout_engine import LayoutEngine
import pygame 
from settings import *
from player import Player
from overlay import Overlay
from sprites import Generic

class Level:
	def __init__(self):

		# get the display surface
		self.display_surface = pygame.display.get_surface()

		# sprite groups
		self.all_sprites = CameraGroup()

		self.setup()
		self.overlay = Overlay(self.player)

	def setup(self):
		self.player = Player((640,360), self.all_sprites)
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
		self.camera_type = 'box_target_camera'

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
			for sprite in self.sprites():
				if sprite.z == layer:
					offset_rect = sprite.rect.copy()
					offset_rect.center -= self.offset
					self.display_surface.blit(sprite.image, offset_rect)

		# pygame.draw.rect(self.display_surface, 'yellow', self.camera_rect, 5)	