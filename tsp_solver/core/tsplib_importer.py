from ..core.city import City

class TSPLibImporter:
    @staticmethod
    def import_instance(filepath: str) -> list[City]:
        """Import a TSPLIB format instance file"""
        cities = []
        reading_coords = False
        city_id = 1

        try:
            with open(filepath, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line == "NODE_COORD_SECTION":
                        reading_coords = True
                        continue
                    if line == "EOF":
                        break
                    if reading_coords:
                        parts = line.split()
                        if len(parts) >= 3:
                            try:
                                x = float(parts[1])
                                y = float(parts[2])
                                cities.append(City(x, y, f"City-{city_id}"))
                                city_id += 1
                            except ValueError:
                                continue

            return cities

        except Exception as e:
            raise Exception(f"Error reading TSPLIB file: {str(e)}")