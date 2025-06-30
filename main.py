import json

def main():
    params = {
    "ofg_pos": -3,
    "resources-cort-1": 30,
    "resources-cort-2": 40,
    "resources-cort-3": 50,
    "resources-cort-4": 50,
    "activity-cort-1": 5,
    "activity-cort-2": 10,
    "activity-cort-3": 15,
    "activity-cort-4": 16,
}
    return json.dumps(params)
    


if __name__ == "__main__":
    print(main())
