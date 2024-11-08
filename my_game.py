import pygame
import random

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

pygame.init()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Сучасний шутер")
clock = pygame.time.Clock()


class Player:
    def __init__(self):
        self.image = pygame.Surface((50, 50))
        self.image.fill((0, 255, 0))
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100))
        self.speed = 5
        self.health = 100
        self.bullets = []
        self.weapon_type = "normal"
        self.shoot_cooldown = 0
        self.jumping = False
        self.jump_count = 10
        self.is_crouching = False
        self.gravity = 0.5
        self.velocity_y = 0

    def update(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_a]:
            self.rect.x -= self.speed
        if keys[pygame.K_d]:
            self.rect.x += self.speed
        if keys[pygame.K_w]:
            self.rect.y -= self.speed
        if keys[pygame.K_s]:
            self.rect.y += self.speed

        if keys[pygame.K_SPACE] and not self.jumping:
            self.jump()

        if keys[pygame.K_f]:
            self.is_crouching = True
            self.rect.height = 25
        else:
            self.is_crouching = False
            self.rect.height = 50

        if self.jumping:
            self.rect.y -= self.velocity_y
            self.velocity_y -= self.gravity

        if self.rect.bottom >= SCREEN_HEIGHT - 50:
            self.jumping = False
            self.rect.bottom = SCREEN_HEIGHT - 50
            self.velocity_y = 0

        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH

        if keys[pygame.K_1]:
            self.weapon_type = "normal"
        if keys[pygame.K_2]:
            self.weapon_type = "fast"
        if keys[pygame.K_3]:
            self.weapon_type = "powerful"

        if pygame.mouse.get_pressed()[0] and self.shoot_cooldown <= 0:
            self.shoot()
            if self.weapon_type == "normal":
                self.shoot_cooldown = 20
            elif self.weapon_type == "fast":
                self.shoot_cooldown = 10
            elif self.weapon_type == "powerful":
                self.shoot_cooldown = 30

        self.shoot_cooldown = max(0, self.shoot_cooldown - 1)
        self.rect.clamp_ip(screen.get_rect())
        self.bullets = [bullet for bullet in self.bullets if bullet.rect.bottom > 0]

    def jump(self):
        if not self.jumping:
            self.jumping = True
            self.velocity_y = self.jump_count

    def shoot(self):
        if self.weapon_type == "normal":
            bullet = Bullet(self.rect.centerx, self.rect.top)
        elif self.weapon_type == "fast":
            bullet = Bullet(self.rect.centerx, self.rect.top, speed=15)
        elif self.weapon_type == "powerful":
            bullet = Bullet(self.rect.centerx, self.rect.top, speed=10, damage=100)
        self.bullets.append(bullet)

    def draw(self):
        screen.blit(self.image, self.rect)
        for bullet in self.bullets:
            bullet.update()
            bullet.draw()


class Enemy:
    def __init__(self, enemy_type):
        self.image = pygame.Surface((50, 50))
        self.rect = self.image.get_rect(center=(random.randint(0, SCREEN_WIDTH), 0))

        if enemy_type == "normal":
            self.image.fill((255, 0, 0))
            self.speed = random.randint(2, 4)
            self.health = 50
        elif enemy_type == "fast":
            self.image.fill((0, 0, 255))
            self.speed = random.randint(4, 6)
            self.health = 30
        elif enemy_type == "strong":
            self.image.fill((255, 165, 0))
            self.speed = random.randint(1, 3)
            self.health = 100

    def update(self, player):
        if self.rect.x < player.rect.x:
            self.rect.x += self.speed / 2
        elif self.rect.x > player.rect.x:
            self.rect.x -= self.speed / 2
        if self.rect.y < player.rect.y:
            self.rect.y += self.speed
        elif self.rect.y > player.rect.y:
            self.rect.y -= self.speed

    def draw(self):
        screen.blit(self.image, self.rect)


class Bullet:
    def __init__(self, x, y, speed=10, damage=50):
        self.image = pygame.Surface((5, 10))
        self.image.fill((255, 255, 0))
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed
        self.damage = damage

    def update(self):
        self.rect.y -= self.speed

    def draw(self):
        screen.blit(self.image, self.rect)


def game_over_screen():
    font = pygame.font.SysFont("Arial", 36)
    game_over_text = font.render("Гра закінчена! Натисніть R для перезапуску або Q для виходу", True, (255, 255, 255))
    screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2))
    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    main()
                elif event.key == pygame.K_q:
                    pygame.quit()
                    quit()


def main():
    player = Player()
    enemies = [Enemy(random.choice(["normal", "fast", "strong"])) for _ in range(5)]
    score = 0
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((0, 0, 0))
        player.update()
        player.draw()

        for enemy in enemies:
            enemy.update(player)
            enemy.draw()

            if enemy.rect.colliderect(player.rect):
                player.health -= 1

            if enemy.rect.top > SCREEN_HEIGHT:
                enemy.rect.center = (random.randint(0, SCREEN_WIDTH), 0)

        for bullet in player.bullets:
            for enemy in enemies:
                if bullet.rect.colliderect(enemy.rect):
                    enemy.health -= bullet.damage
                    player.bullets.remove(bullet)
                    if enemy.health <= 0:
                        enemies.remove(enemy)
                        score += 10
                        enemies.append(Enemy(random.choice(["normal", "fast", "strong"])))


        health_text = pygame.font.SysFont("Arial", 24).render(f"Health: {player.health}", True, (255, 255, 255))
        screen.blit(health_text, (10, 10))

        score_text = pygame.font.SysFont("Arial", 24).render(f"Score: {score}", True, (255, 255, 255))
        screen.blit(score_text, (10, 40))

        if player.health <= 0:
            running = False
            game_over_screen()

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
