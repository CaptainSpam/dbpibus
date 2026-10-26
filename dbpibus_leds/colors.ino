#include <Adafruit_NeoPixel.h>

void get_shift_colors(int shift, int *arr, int size) {
  // So my C/C++ is a bit rusty, which is why this is kinda jank, but I THINK
  // this is a reasonable way to populate an array using values from a choice of
  // five different arrays...
  for(int i = 0; i < size; i++) {
    int in = i % IDLE_COLORS_ARR_LEN;

    switch(shift) {
      case SHIFT_DAWNGUARD:
        arr[in] = IDLE_COLORS_DAWNGUARD[in];
        break;
      case SHIFT_ALPHAFLIGHT:
        arr[in] = IDLE_COLORS_ALPHAFLIGHT[in];
        break;
      case SHIFT_NIGHTWATCH:
        arr[in] = IDLE_COLORS_NIGHTWATCH[in];
        break;
      case SHIFT_ZETASHIFT:
        arr[in] = IDLE_COLORS_ZETASHIFT[in];
        break;
      case SHIFT_OMEGASHIFT:
        arr[in] = IDLE_COLORS_OMEGASHIFT[in];
        break;
      default:
        arr[in] = 0;
    }
  }
}

int blend_colors(int color_a, int color_b, float amount) {
  // CLAMP!
  if(amount < 0.0) amount = 0.0;
  if(amount > 1.0) amount = 1.0;

  // DECOMPOSE!
  int red_a = (color_a >> 16) & 0xff;
  int green_a = (color_a >> 8) & 0xff;
  int blue_a = color_a & 0xff;

  int red_b = (color_b >> 16) & 0xff;
  int green_b = (color_b >> 8) & 0xff;
  int blue_b = color_b & 0xff;

  // INTERPOLATE!
  int red = red_a + (red_b - red_a) * amount;
  int green = green_a + (green_b - green_a) * amount;
  int blue = blue_a + (blue_b - blue_a) * amount;

  // RETURN!
  return Adafruit_NeoPixel::Color(red, green, blue);
}
