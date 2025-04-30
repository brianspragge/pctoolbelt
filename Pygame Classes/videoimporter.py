import cv2  # Import OpenCV for video handling
import pygame

class VideoImporter:
    """
    Handles importing and displaying videos for use in program.
    Example:
    def __init__(self):
        pygame.init()
        self.screen_width = 1600
        self.screen_height = 900
        self.screen = pygame.display.set_mode(
            (self.screen_width, self.screen_height))
        self.video_importer = VideoImporter(
            '/path/to/video.mp4', scaling_factor=1.0, buffer_size=3)

    def run_program(self):
        self.video_importer.display_video_frame(
            self.screen, self.screen_width, self.screen_height)

    def quit_program(self):
        self.video_importer.cap.release()
    """

    def __init__(self, video_path):
        """Initialize the video capture and other attributes."""
        self.cap = cv2.VideoCapture(video_path)
        self.last_surface = None  # Cache the last Pygame surface

    def display_video_frame(self, screen, screen_width, screen_height):
        """
        Retrieve and display the next frame of the video on the provided screen.
        Loop the video when it ends.
        """
        ret, video_frame = self.cap.read()
        if not ret:
            # Video has ended, reset to the beginning
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Reset to the first frame
            ret, video_frame = self.cap.read()  # Read the first frame again

        if ret:
            # Flip the video frame horizontally before formatting
            video_frame = cv2.flip(video_frame, 1)  # 1 means flipping around the y-axis
            self.format_video(video_frame, screen, screen_width, screen_height)

    def format_video(self, video, screen, screen_width, screen_height):
        """Resize and display the video to completely fill the screen."""
        # Convert the BGR frame to RGB
        frame = cv2.cvtColor(video, cv2.COLOR_BGR2RGB)

        # Avoid resizing if the frame size already matches
        resized_frame = self.resize_frame_to_fill_screen(
            frame, screen_width, screen_height)
        self.blit_frame(resized_frame, screen, screen_width, screen_height)

    def resize_frame_to_fill_screen(self, frame, screen_width, screen_height):
        video_height, video_width = frame.shape[:2]
        video_aspect_ratio = video_width / video_height
        screen_aspect_ratio = screen_width / screen_height

        if video_aspect_ratio > screen_aspect_ratio:
            new_height = screen_height
            new_width = int(new_height * video_aspect_ratio)
        else:
            new_width = screen_width
            new_height = int(new_width / video_aspect_ratio)

        # Use INTER_CUBIC for better quality when resizing
        return cv2.resize(
            frame, (new_width, new_height), interpolation=cv2.INTER_AREA)

    def blit_frame(self, frame, screen, screen_width, screen_height):
        """
        Convert and display the resized frame, cropping it to fit the screen.
        """
        # Convert to Pygame surface only if frame is new
        if self.last_surface is None or frame.shape != self.last_surface.get_size():
            self.last_surface = pygame.surfarray.make_surface(frame)

        # Calculate the cropping offsets to center the frame on the screen
        x_offset = (frame.shape[1] - screen_width) // 2
        y_offset = (frame.shape[0] - screen_height) // 2

        # Blit the cached surface
        screen.blit(
            pygame.transform.rotate(self.last_surface, -90),
            (-x_offset, -y_offset)
        )
