'''
Created on Oct 16, 2018

@author: kwang66
'''
from graph.api import api
import unittest
import json
from unittest import TestCase

class TestApi(TestCase):

    def setUp(self):
        self.api = api.test_client()
    
    def test_filtered_actors(self):
        response = self.api.get('/actors?age=62')
        data=json.loads(response.get_data())
        for item in data:
            self.assertEqual(62, list(item.values())[0]["age"])
    
    def test_filtered_movies(self):
        response = self.api.get('/movies?year=2003')
        data=json.loads(response.get_data())
        for item in data:
            self.assertEqual(2003, list(item.values())[0]["year"])
    
    def test_get_actor(self):
        response = self.api.get('/actors/Bruce_Willis')
        data=json.loads(response.get_data())
        self.assertEqual("Bruce_Willis",data["name"])

    def test_get_movie(self):
        response = self.api.get('/movies/Unbreakable')
        data=json.loads(response.get_data())
        self.assertEqual("Unbreakable",data["name"])
    
    def test_put_actor(self):
        data={}
        data["age"]=63
        response = self.api.put('/actors/Bruce_Willis',data=json.dumps(data),content_type='application/json')
        data=json.loads(response.get_data())
        self.assertEqual(63,data["age"])
        response = self.api.get('/actors/Bruce_Willis')
        data=json.loads(response.get_data())
        self.assertEqual(63,data["age"])
    
    def test_put_movie(self):
        data={}
        data["box_office"]=50000
        response = self.api.put('/movies/Unbreakable',data=json.dumps(data),content_type='application/json')
        data=json.loads(response.get_data())
        self.assertEqual(50000,data["box_office"])
        response = self.api.get('/movies/Unbreakable')
        data=json.loads(response.get_data())
        self.assertEqual(50000,data["box_office"])
    
    def test_post_actor(self):
        data={}
        data["age"]=50
        data["name"]="Made_Up"
        data["total_gross"]=50000
        data["movies"]=["The_Player"]
        response = self.api.post('/actors',data=json.dumps(data),content_type='application/json')
        data=json.loads(response.get_data())
        self.assertEqual(50000,data["total_gross"])
        self.assertEqual("Made_Up",data["name"])
        response = self.api.get('/actors/Made_Up')
        data=json.loads(response.get_data())
        self.assertEqual(data["movies"][0], "The_Player")
    
    def test_post_movie(self):
        data={}
        data["year"]=1823
        data["name"]="Made_Up"
        data["box_office"]=50000
        data["actors"]=["The_Player"]
        response = self.api.post('/movies',data=json.dumps(data),content_type='application/json')
        data=json.loads(response.get_data())
        self.assertEqual(50000,data["box_office"])
        self.assertEqual("Made_Up",data["name"])
        response = self.api.get('/movies/Made_Up')
        data=json.loads(response.get_data())
        self.assertEqual(data["actors"][0], "The_Player")
        
    def test_delete_actor(self):
        response = self.api.delete('/actors/John_Cusack')
        data=json.loads(response.get_data())
        self.assertEqual("deleted",data["success"])
        response = self.api.get('/actors/John_Cusack')
        data=json.loads(response.get_data())
        self.assertEqual("Content Not found",data["error"])
        
    def test_delete_movie(self):
        response = self.api.delete('/movies/The_Bye_Bye_Man')
        data=json.loads(response.get_data())
        self.assertEqual("deleted",data["success"])
        response = self.api.get('/movies/The_Bye_Bye_Man')
        data=json.loads(response.get_data())
        self.assertEqual("Content Not found",data["error"])
    

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()