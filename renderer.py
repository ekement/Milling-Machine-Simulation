import glfw
import moderngl
import numpy as np
from pyrr import Matrix44
from shaders import *
import math

class Renderer:
    def __init__(self, vertices):
        if not glfw.init():
            raise('Could not initialize GLFW')
        self.window = glfw.create_window(800, 600, "Machining Simulation", None, None)
        if not self.window:
            glfw.terminate()
            raise('Could not create rendering window')

        glfw.make_context_current(self.window)
        self.ctx = moderngl.create_context()

        self.prog = self.ctx.program(vertex_shader=vertex_shader_source_unlit, fragment_shader=fragment_shader_source_unlit)


        #vertices = np.array([[ 0, 0, 0],
        #                    [10, 0, 0],
        #                    [0, 10, 0]])

        self.vbo = self.ctx.buffer(vertices.astype('f4').tobytes(), dynamic=True)
        self.vao = self.ctx.simple_vertex_array(self.prog, self.vbo, 'position', 'color')






    def run(self):
        while not glfw.window_should_close(self.window):
            self.buffer_width, self.buffer_height = glfw.get_framebuffer_size(self.window)
            self.ctx.viewport = (0, 0, self.buffer_width, self.buffer_height)

            radius = 400.0
            camX = math.cos(glfw.get_time()/2) * radius
            camZ = math.sin(glfw.get_time()/2) * radius

            proj = Matrix44.perspective_projection(20.0, self.buffer_width/self.buffer_height, 0.1, 1000.0)
            #lookat = Matrix44.look_at(
            #    (-camX, -camZ, 200),
            #    (60.0, 30.0, 30.0),
            #    (0.0, 0.0, 1.0),
            #)

            lookat = Matrix44.look_at(
                (-150, -200, 250),
                (20.0, 0.0, 30.0),
                (0.0, 0.0, 1.0),
            )
            #richtige perspektive
            # (-200, -200, 200),
            #(20.0, 0.0, 30.0),
            # (0.0, 0.0, 1.0),
            #

            modelViewProjection = proj * lookat

            self.ctx.clear(0.1, 0.15, 0.2, 0.0)
            self.ctx.enable(moderngl.DEPTH_TEST)

            self.prog['modelViewProj'].write(modelViewProjection.astype('f4').tobytes())

            self.vao.render(moderngl.TRIANGLES)
            glfw.swap_buffers(self.window)
            #glfw.wait_events()
            glfw.poll_events()

        glfw.terminate()



    # if __name__ == '__main__':
# #    renderer = Renderer()
# #    renderer.run()