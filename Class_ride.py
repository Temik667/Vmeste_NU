from math import cos, asin, sqrt, pi, radians, sin, atan2, degrees
import requests
import asyncio

request = {}

class Requests():

    @classmethod
    def print_request(cls, user_id):
        print(request[user_id])

    @classmethod
    def add_request(cls, user_id) -> None:
        request.update({user_id: {}})
    
    @classmethod
    def add_a_point(cls, user_id, lat1, long1) -> None:
        request[user_id]['lat1'] = lat1
        request[user_id]['long1'] = long1
    
    @classmethod
    def add_b_point(cls, user_id, lat2, long2) -> None:
        request[user_id]['lat2'] = lat2
        request[user_id]['long2'] = long2
    
    @classmethod
    def add_others(cls, user_id, num, name, sex) -> None:
        request[user_id]['num'] = num
        request[user_id]['name'] = name
        request[user_id]['sex'] = sex

    @staticmethod
    def remove_request(user_id) -> None:
        del request[user_id]
    
    @staticmethod
    def calc_dis(lat1, long1, lat2, long2) -> int:
        p = pi/180
        a = 0.5 - cos((lat2-lat1)*p)/2 + cos(lat1*p) * cos(lat2*p) * (1-cos((long2-long1)*p))/2
        return 12742 * asin(sqrt(a))
    
    @staticmethod
    def midpoint(x1, y1, x2, y2):
        lat1 = radians(x1)
        lon1 = radians(y1)
        
        lat2 = radians(x2)
        lon2 = radians(y2)

        bx = cos(lat2) * cos(lon2 - lon1)
        by = cos(lat2) * sin(lon2 - lon1)
        lat3 = atan2(sin(lat1) + sin(lat2), \
           sqrt((cos(lat1) + bx) * (cos(lat1) \
           + bx) + by**2))
        lon3 = lon1 + atan2(by, cos(lat1) + bx)

        return [round(degrees(lat3), 6), round(degrees(lon3), 6)]
    
    @staticmethod
    def price(long1, lat1, long2, lat2):
        statement = "https://taxi-routeinfo.taxi.yandex.net/taxi_info?clid=ak220204&apikey=dYZrZRPyvsbzAvjEDhowQZwJIAHGvYZiWFdfRBXs&rll={},{}~{},{}&class=econom&currency=KZT".format(str(lat1), str(long1), str(lat2), str(long2))
        response = requests.get(statement).json()
        fin = response['options']
        result = fin[0]
        return int(result['price'])

    @classmethod
    def showNearest(cls, user_id) -> list:
        result = {}

        arr = request[user_id]
        lat1 = arr['lat1']
        long1 = arr['long1']
        dlat1 = arr['lat2']
        dlong1 = arr['long2']
        num1 = arr['num']

        
        for i in request:
            if i != user_id:
                arr1 = request[i]
                lat2 = arr1['lat1']
                long2 = arr1['long1']
                dlat2 = arr1['lat2']
                dlong2 = arr1['long2']
                num2 = arr1['num']
                name = arr1['name']
                sex = arr1['sex']

                if cls.calc_dis(lat1, long1, lat2, long2) <=2 and num1 + num2 <= 3:
                    dep = cls.midpoint(lat1, long1, lat2, long2)
                    des = cls.midpoint(dlat1, dlong1, dlat2, dlong2)
                    result.update({i: {'name': name, 'sex': sex, 'price': cls.price(dep[0], dep[1], des[0], des[1]), 'num': num2}})
    
        return result
    
    @classmethod
    def match(cls, user_id, user_id_2) -> None:
        cls.remove_request(user_id)
        cls.remove_request(user_id_2)