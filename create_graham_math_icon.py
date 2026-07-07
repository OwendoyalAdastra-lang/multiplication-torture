#!/usr/bin/env python3
"""Create a simple app icon for Multiplication Torture."""

import os
import sys

import pygame

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "graham_math_icon.png")
SIZE = 256

pygame.init()
surface = pygame.Surface((SIZE, SIZE), pygame.SRCALPHA)
surface.fill((18, 24, 52, 255))
pygame.draw.rect(surface, (36, 48, 92, 255), pygame.Rect(18, 18, SIZE - 36, SIZE - 36), border_radius=42)
pygame.draw.rect(surface, (90, 220, 255, 255), pygame.Rect(18, 18, SIZE - 36, SIZE - 36), width=6, border_radius=42)
pygame.draw.circle(surface, (255, 196, 72, 255), (62, 62), 28)
pygame.draw.circle(surface, (95, 235, 150, 255), (SIZE - 70, 70), 22)

font_big = pygame.font.SysFont("DejaVu Sans", 72, bold=True)
font_small = pygame.font.SysFont("DejaVu Sans", 34, bold=True)
surface.blit(font_big.render("8×6", True, (255, 230, 90, 255)), font_big.render("8×6", True, (255, 230, 90, 255)).get_rect(center=(SIZE // 2, 118)))
surface.blit(font_small.render("Torture", True, (245, 248, 255, 255)), font_small.render("Torture", True, (245, 248, 255, 255)).get_rect(center=(SIZE // 2, 188)))

pygame.image.save(surface, OUT)
pygame.quit()
print(f"Created {OUT}")