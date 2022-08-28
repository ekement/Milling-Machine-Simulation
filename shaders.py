vertex_shader_source_unlit = """
#version 330
uniform mat4 modelViewProj;
in vec3 position;
in vec3 color;
out vec4 vertexColor;

void main() {
	gl_Position = modelViewProj * vec4(position, 1.0);
	vertexColor = vec4(color, 1);
}"""

fragment_shader_source_unlit = """
#version 330
in vec4 vertexColor;
out vec4 fragColor;

void main(void) {
	fragColor = vertexColor;
}"""
