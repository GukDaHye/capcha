# Bus Congestion Monitoring System

This project monitors bus stop congestion levels in real-time using Django. Below are the steps to set up the project, including recent updates to the `BusStop` model and data generation scripts.

---

## Features
- Tracks bus stop congestion with live updates.
- Supports multiple bus stops with customizable capacities.
- Generates fake data for testing and development.

---

## Recent Updates

### 1. `BusStop` Model Update
The `BusStop` model now includes a `capacity` field to specify the maximum number of students a bus can accommodate.

#### Updated `BusStop` Model
```python
class BusStop(models.Model):
    stop_id = models.AutoField(primary_key=True)
    location = models.CharField(max_length=200, blank=True, null=True)  # Optional GPS coordinates
    name = models.CharField(max_length=100)
    capacity = models.IntegerField(default=0)  # Maximum capacity

    def __str__(self):
        return self.name
