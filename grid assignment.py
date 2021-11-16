import pygame
import math 
from queue import PriorityQueue

WIDTH = 400		# SIZE OF DISPLAY
disp = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("A* Algorithm Path Finding")

RED = (255, 0, 0)
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BROWN = (165, 42, 42)
ORANGE = (255, 165 ,0)
GRAY = (128, 128, 128)
TURQUOISE = (64, 224, 208)

class Spot:
	def __init__(self, row, col, width, total_rows):
		self.row = row
		self.col = col
		self.x = row * width
		self.y = col * width
		self.color = WHITE
		self.neighbors = []
		self.width = width
		self.total_rows = total_rows

	def get_pos(self):
		return self.row, self.col

	def is_closed(self):
		return self.color == RED

	def is_open(self):
		return self.color == BROWN

	def is_barrier(self):
		return self.color == BLACK

	def is_start(self):
		return self.color == ORANGE

	def is_goal(self):
		return self.color == TURQUOISE

	def reset(self):
		self.color = WHITE

	def make_start(self):
		self.color = ORANGE

	def make_closed(self):
		self.color = RED

	def make_open(self):
		self.color = BROWN

	def make_barrier(self):
		self.color = BLACK

	def make_goal(self):
		self.color = TURQUOISE

	def make_path(self):
		self.color = GREEN

	def draw(self, disp):
		pygame.draw.rect(disp, self.color, (self.x, self.y, self.width, self.width))

	def update_neighbors(self, grid):
		self.neighbors = []
		if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier(): # DOWN
			self.neighbors.append(grid[self.row + 1][self.col])

		if self.row > 0 and not grid[self.row - 1][self.col].is_barrier(): # UP
			self.neighbors.append(grid[self.row - 1][self.col])

		if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier(): # RIGHT
			self.neighbors.append(grid[self.row][self.col + 1])

		if self.col > 0 and not grid[self.row][self.col - 1].is_barrier(): # LEFT
			self.neighbors.append(grid[self.row][self.col - 1])

	def __lt__(self, other):
		return False


def h(p1, p2):
	x1, y1 = p1
	x2, y2 = p2
	return abs(x1 - x2) + abs(y1 - y2)


def make_path(came_from, current, draw):
	while current in came_from:
		current = came_from[current]
		current.make_path()
		draw()


def astar_algorithm(draw, grid, start, goal):
	count = 0
	open_set = PriorityQueue()
	open_set.put((0, count, start))
	came_from = {}
	g_score = {spot: float("inf") for row in grid for spot in row}
	g_score[start] = 0
	f_score = {spot: float("inf") for row in grid for spot in row}
	f_score[start] = h(start.get_pos(), goal.get_pos())

	open_set_hash = {start}

	while not open_set.empty():
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()

		current = open_set.get()[2]
		open_set_hash.remove(current)

		if current == goal:
			make_path(came_from, goal, draw)
			goal.make_goal()
			return True

		for neighbor in current.neighbors:
			temp_g_score = g_score[current] + 1

			if temp_g_score < g_score[neighbor]:
				came_from[neighbor] = current
				g_score[neighbor] = temp_g_score
				f_score[neighbor] = temp_g_score + h(neighbor.get_pos(), goal.get_pos())
				if neighbor not in open_set_hash:
					count += 1
					open_set.put((f_score[neighbor], count, neighbor))
					open_set_hash.add(neighbor)
					neighbor.make_open()

		draw()

		if current != start:
			current.make_closed()

	return False


def make_grid(rows, width):
	grid = []
	gap = width // rows
	for i in range(rows):
		grid.append([])
		for j in range(rows):
			spot = Spot(i, j, gap, rows)
			grid[i].append(spot)

	return grid


def draw_grid(disp, rows, width):
	gap = width // rows
	for i in range(rows):
		pygame.draw.line(disp, GRAY, (0, i * gap), (width, i * gap))
		for j in range(rows):
			pygame.draw.line(disp, GRAY, (j * gap, 0), (j * gap, width))


def draw(disp, grid, rows, width):
	disp.fill(WHITE)

	for row in grid:
		for spot in row:
			spot.draw(disp)

	draw_grid(disp, rows, width)
	pygame.display.update()


def get_clicked_pos(pos, rows, width):
	gap = width // rows
	y, x = pos

	row = y // gap
	col = x // gap

	return row, col


def main(disp, width):
	Grid_Size = 10			# GRID SIZE THAT CAN BE CHANGE
	grid = make_grid(Grid_Size, width)

	start = None
	goal = None

	run = True
	while run:
		draw(disp, grid, Grid_Size, width)
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False

			if pygame.mouse.get_pressed()[0]: # LEFT MOUSE CLICK TO REMOVE START, GOAL AND BARRIER 
				pos = pygame.mouse.get_pos()
				row, col = get_clicked_pos(pos, Grid_Size, width)
				spot = grid[row][col]
				if not start and spot != goal:
					start = spot
					start.make_start()

				elif not goal and spot != start:
					goal = spot
					goal.make_goal()

				elif spot != goal and spot != start:
					spot.make_barrier()

			elif pygame.mouse.get_pressed()[2]:		# RIGHT MOUSE CLICK TO ADD START FIRST, GOAL SECOND AND THE REST IS BARRIER
				pos = pygame.mouse.get_pos()
				row, col = get_clicked_pos(pos, Grid_Size, width)
				spot = grid[row][col]
				spot.reset()
				if spot == start:
					start = None
				elif spot == goal:
					goal = None

			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_SPACE and start and goal:	# START FINDING THE PATH BY CLICKING SPACE KEY
					for row in grid:
						for spot in row:
							spot.update_neighbors(grid)

					astar_algorithm(lambda: draw(disp, grid, Grid_Size, width), grid, start, goal)

				if event.key == pygame.K_c:		# CLEAR THE DISPLAY BY CLICKING C KEY
					start = None
					goal = None
					grid = make_grid(Grid_Size, width)

	pygame.quit()

main(disp, WIDTH)
