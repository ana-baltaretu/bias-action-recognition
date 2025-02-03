from typing import Callable, Dict
import numpy as np


class PlanePointGenerator:
    def __init__(self, center: np.ndarray, normal: np.ndarray, width: float, height: float, num_points: int):
        """
        Initialize the PlanePointGenerator with shared attributes.

        :param center: Center of the plane as a numpy array [x, y, z].
        :param normal: Normal vector of the plane as a numpy array [nx, ny, nz].
        :param width: Width of the plane.
        :param height: Height of the plane.
        :param num_points: Number of points to generate.
        """
        self.center = center
        self.normal = normal / np.linalg.norm(normal)  # Normalize the normal vector
        self.width = width
        self.height = height
        self.num_points = num_points

        # Define strategies
        self.strategies: Dict[str, Callable[[], np.ndarray]] = {
            "random": self.random_points_on_rotated_plane,
            "grid": self.evenly_distributed_points_on_rotated_plane,
            "poisson": self.poisson_disk_sampling_on_rotated_plane,
        }

    def random_points_on_rotated_plane(self) -> np.ndarray:
        arbitrary = np.array([1, 0, 0]) if not np.allclose(self.normal, [1, 0, 0]) else np.array([0, 1, 0])
        u = np.cross(self.normal, arbitrary)
        u = u / np.linalg.norm(u)
        v = np.cross(self.normal, u)
        v = v / np.linalg.norm(v)

        local_x = np.random.uniform(-self.width / 2, self.width / 2, self.num_points)
        local_y = np.random.uniform(-self.height / 2, self.height / 2, self.num_points)

        points = [self.center + x * u + y * v for x, y in zip(local_x, local_y)]
        return np.array(points)

    def evenly_distributed_points_on_rotated_plane(self) -> np.ndarray:
        arbitrary = np.array([1, 0, 0]) if not np.allclose(self.normal, [1, 0, 0]) else np.array([0, 1, 0])
        u = np.cross(self.normal, arbitrary)
        u = u / np.linalg.norm(u)
        v = np.cross(self.normal, u)
        v = v / np.linalg.norm(v)

        grid_size = int(np.sqrt(self.num_points))
        x_coords = np.linspace(-self.width / 2, self.width / 2, grid_size)
        y_coords = np.linspace(-self.height / 2, self.height / 2, grid_size)

        points = [self.center + x * u + y * v for x in x_coords for y in y_coords]
        return np.array(points)

    def poisson_disk_sampling_on_rotated_plane(self, min_distance=1.4, num_attempts=30) -> np.ndarray:
        arbitrary = np.array([1, 0, 0]) if not np.allclose(self.normal, [1, 0, 0]) else np.array([0, 1, 0])
        u = np.cross(self.normal, arbitrary)
        u = u / np.linalg.norm(u)
        v = np.cross(self.normal, u)
        v = v / np.linalg.norm(v)

        active_list = []
        points = []

        first_point_local = np.array([
            np.random.uniform(-self.width / 2, self.width / 2),
            np.random.uniform(-self.height / 2, self.height / 2)
        ])
        first_point = self.center + first_point_local[0] * u + first_point_local[1] * v
        points.append(first_point)
        active_list.append(first_point)

        while active_list:
            if len(points) >= self.num_points:
                break

            current_point = active_list.pop(np.random.randint(len(active_list)))

            for _ in range(num_attempts):
                if len(points) >= self.num_points:
                    break

                angle = np.random.uniform(0, 2 * np.pi)
                radius = np.random.uniform(min_distance, 2 * min_distance)
                offset_local = np.array([np.cos(angle) * radius, np.sin(angle) * radius])

                new_point_local = np.array([
                    (current_point - self.center).dot(u) + offset_local[0],
                    (current_point - self.center).dot(v) + offset_local[1]
                ])

                if (-self.width / 2 <= new_point_local[0] <= self.width / 2) and (-self.height / 2 <= new_point_local[1] <= self.height / 2):
                    new_point = self.center + new_point_local[0] * u + new_point_local[1] * v

                    if all(np.linalg.norm(new_point - p) >= min_distance for p in points):
                        points.append(new_point)
                        active_list.append(new_point)

        return np.array(points)

    def generate_points(self, strategy: str, **kwargs) -> np.ndarray:
        """
        Generate points using the specified strategy.

        :param strategy: The name of the strategy to use ('random', 'grid', 'poisson').
        :param kwargs: Additional keyword arguments for the selected strategy.
        :return: List of generated points.
        """
        if strategy not in self.strategies:
            raise ValueError(f"Strategy '{strategy}' is not valid. Choose from {list(self.strategies.keys())}.")
        return self.strategies[strategy](**kwargs)


# Example usage
if __name__ == "__main__":
    center = np.array([0, 0, 0])
    normal = np.array([0, 0, 1])
    width, height = 4, 4
    num_points = 10

    generator = PlanePointGenerator(center, normal, width, height, num_points)
    strategy = "poisson"  # Choose a strategy: 'random', 'grid', or 'poisson'
    points = generator.generate_points(strategy)
    print("Generated Points:")
    for point in points:
        print(point)
