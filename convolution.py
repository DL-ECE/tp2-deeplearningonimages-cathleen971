# -*- coding: utf-8 -*-
"""Copie de convolution.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1UrDEQLjac5fFKPJDFTHrZBNBuWhp0adW

# TP-2 Deep Learning on Images
"""

# Import the different module we will need in this notebook
import os

# To read and compute on Images: imageio [imageio doc](https://imageio.readthedocs.io/en/stable/)
# To create some plot and figures: matplolib [matplotlib doc](https://matplotlib.org/)
# To do computation on matrix and vectors: numpy [numpy doc](https://numpy.org/)
import imageio
import matplotlib.pyplot as plt
import numpy as np

# To do computation on matrix and vectors and automatic differenciation: pytorch [torch doc](https://pytorch.org/docs/stable/index.html)
import torch
import torch.nn as nn
import torch.optim as optim
from torch.nn import functional as F
from torch.utils.data import DataLoader

# To do some computation on images with pytorch direclty on the GPU [torchvision doc](https://pytorch.org/vision)
from torchvision import transforms
from torchvision.datasets import MNIST, FashionMNIST
import random
import tqdm.notebook as tq

# To get the same data as TP1 
from sklearn.datasets import fetch_openml
from sklearn.model_selection import train_test_split
# enable tpu computation
# !curl https://raw.githubusercontent.com/pytorch/xla/master/contrib/scripts/env-setup.py -o pytorch-xla-env-setup.py
# !python pytorch-xla-env-setup.py --version nightly --apt-packages libomp5 libopenblas-dev

"""## Clothes images classification using Fashion-MNIST dataset

In this notebook you will train your second and even third neural network. 

Feel free to look back at the Lecture-2 slides to complete the cells below.



All the dependencies are installed. Below we import them and will be using them in all our notebooks.
Please feel free to look arround and look at their API.
The student should be limited to these imports to complete this work.
"""

# In order to have some reproducable results and easier debugging 
# we fix the seed of random.
random.seed(1342)
np.random.seed(1342)
torch.manual_seed(1342)
torch.cuda.manual_seed_all(1342)

import builtins as __builtin__
def print(*args, **kwargs):
    """My custom print() function."""
    return __builtin__.print(*args, **kwargs, end='\n\n')

"""## Refresh on numpy and images"""

# Let's do again basics of numpy 
mat_numpy = np.arange(15).reshape(3, 5)
print(mat_numpy) # Create a vector from 0 to 14 and reshape it into a Matrix 3X5

print(mat_numpy.shape) # Return the size of the matrix (3, 5)

print(mat_numpy[0]) # Return the first row of the matrix 

print(mat_numpy[0,3]) # Return first row and 4th column  element 

# Also interesting with higher dimension 
# Below can be though of 2 3X4 matrix 
tensor = np.zeros((2,3,4))   # Create an tensor of shape [2,2,2] of all zeros
print(tensor)                # Prints [[[0. 0. 0. 0.]
                             #          [0. 0. 0. 0.]
                             #          [0. 0. 0. 0.]]
                             #        [[0. 0. 0. 0.]
                             #         [0. 0. 0. 0.]
                             #         [0. 0. 0. 0.]]]

"""Now it's your turn create a function that return a tensor of shape 
n_rowsxn_columsxn_channels that contains a default value every where
"""

def build_image_like_tensor(n_rows:int, n_colums: int, n_channels:int, default_value: int)-> np.ndarray:
  """Create a tensor of 3 dimension. 
     It should have a shape similar to (n_rows, n_colums, n_channels)
     It should be containing the default value set by default_value
  """
  # YOUR CODE HERE
  tensor = np.full((n_rows,n_colums,n_channels),fill_value=default_value)
  return tensor

test =build_image_like_tensor(16,16,3,255)
  print(test)

# Create 3 different tensors with the above function containing different value between [0,255]
# Uncomment the 3 line below and complete with your answer 
white_like = build_image_like_tensor(16,16,3,255)
gray_like = build_image_like_tensor(14,14,4,198)
black_like = build_image_like_tensor(16,16,3,0)

# Each of the tensor that you have created can be seen as an image. Use here is the way to display it using matplotlib imshow:
def plot_one_tensor(image_tensor: np.array):
    """Function to plot the image tensor"""
    plt.imshow(image_tensor, cmap='RdBu')

plot_one_tensor(white_like)

plot_one_tensor(gray_like)

plot_one_tensor(black_like)

"""We saw that an digital image is the combination of a 3 channel tensor RGB. 
Each channel represent respectively the R red componant, G greed componant, B blue componant.
"""

# Create again 3 image tensors with your function
# Then change them to be representing a red, a green, a blue image
# Uncomment the 3 line below and complete with your answer 


red_like = build_image_like_tensor(16,16,3,(255,0,0))
green_like = build_image_like_tensor(16,16,3,(0,255,0))
blue_like = build_image_like_tensor(16,16,3,(0,0,255))

plot_one_tensor(red_like)

plot_one_tensor(green_like)

plot_one_tensor(blue_like)

"""## What Pytorch can do

*   Similar functions to Numpy on GPU
*   Calculate automatically gradient on the neural network
*   Some neural networks layers are already coded : dense, convolution, pooling, etc
*   Calculate automatically the weights update
*   Provide optimizer to compute gradient descent
"""

mat_torch = torch.arange(15).reshape(3,5)

print(mat_torch) # Create a vector from 0 to 14 and reshape it into a Matrix 3X5
print(mat_torch.shape) # Return the size of the matrix (3, 5)
print(mat_torch[0]) # Return the first row of the matrix 
print(mat_torch[0,3]) # Return first row and 4th column element 
# This was easy but everything was on the CPU so it's the same as Numpy 
# To do computation on the GPU (graphic card calculation can be 50x faster)

# What is the GPU on this machine ? 
# !nvidia-smi
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
device

mat_torch = torch.arange(15, device=device).reshape(3,5)
print(mat_torch) # Create a vector from 0 to 14 and reshape it into a Matrix 3X5
print(mat_torch.shape) # Return the size of the matrix (3, 5)
print(mat_torch[0]) # Return the first row of the matrix 
print(mat_torch[0,3]) # Return first row and 4th column element

"""Let's say we want a faster sigmoid and softmax. 
We can use the same function from TP-1
"""

def normalize_tensor(input_tensor: torch.Tensor) -> torch.Tensor:
    """Apply a normalization to the tensor"""
    normalized_dataset =(input_tensor -torch.min(input_tensor)) / (torch.max(input_tensor)-torch.min(input_tensor))
    return normalized_dataset
   

def sigmoid(input_tensor: torch.Tensor) -> torch.Tensor:
    """Apply a sigmoid to the input Tensor"""
    sig = 1/(1 +torch.exp(-input_tensor))
    return sig

def softmax(input_tensor: torch.Tensor)-> torch.Tensor:
    """Apply a softmax to the input tensor"""
    Smax = torch.exp(input_tensor)/torch.sum(torch.exp(input_tensor),axis=1).reshape(-1,1)
    return Smax

def target_to_one_hot(targets: torch.Tensor, num_classes=10) -> torch.Tensor:
    """Create the one hot representation of the target""" 
    one_hot_matrix = np.zeros((70000,num_classes))
    ###
    for i in range(0,targets.shape[0]):
      label = int(targets[i])
      one_hot_matrix[i,label]=1
      
    return one_hot_matrix

# However as mention above pytorch already has some built-ins function 

# sigmoid function [sigmoid doc](https://pytorch.org/docs/stable/generated/torch.nn.Sigmoid.html?highlight=sigmoid#torch.nn.Sigmoid)
# softmax function [softmax doc](https://pytorch.org/docs/stable/generated/torch.nn.Softmax.html?highlight=softmax#torch.nn.Softmax)

mat_torch = torch.arange(15, dtype=torch.float64, device=device).reshape(3,5)
# Uncomment the line bellow to check if your implementation is correct

assert torch.allclose(sigmoid(mat_torch), torch.sigmoid(mat_torch))
print(sigmoid(mat_torch))
print(torch.sigmoid(mat_torch))

assert torch.allclose(softmax(mat_torch),torch.softmax(mat_torch,dim=1))
print(softmax(mat_torch))
print(torch.softmax(mat_torch, dim=1))

"""## Transforming our Neural network from TP1"""

if __name__ == "__main__":
    # Downloading again the same MNIST dataset 

    mnist_data, mnist_target = fetch_openml('mnist_784', version=1, return_X_y=True)
    X_train, X_test, y_train, y_test = train_test_split(mnist_data, mnist_target, test_size=0.33, random_state=1342)
    # Change the input data to be normalize and target data to be correctly encoded 

    X_train = torch.from_numpy(X_train.astype(np.float32))
    X_train = normalize_tensor(X_train)

    X_test = torch.from_numpy(X_test.astype(np.float32))
    X_test = normalize_tensor(X_test)
 
    y_train = torch.from_numpy(y_train.astype(np.int32))
    y_train = target_to_one_hot(y_train)
    
    y_test = torch.from_numpy(y_test.astype(np.int32))
    y_test = target_to_one_hot(y_test)

"""Your remember the famous `class FFNN` from **TP1** ?? 

Here we will create the same version but with pytorch and we will see the power of this framework. 

Auto calculation of the backward pass and auto update of the weights 🎉

In pytorch a dense layer similar to our `Class Layer` is a called **Linear Layer**

[linear layer documentation] -> https://pytorch.org/docs/stable/generated/torch.nn.Linear.html#torch.nn.Linear
"""

class FFNN(nn.Module):
    def __init__(self, config, device, minibatch_size=100, learning_rate=0.01, momentum=0):
        super().__init__()
        self.layers = []
        self.nlayers = len(config)
        self.minibatch_size = minibatch_size
        self.learning_rate = learning_rate
        self.momentum = momentum
        self.device = device 

        # We use the built-in activation functions
        # TODO: Maybe try with another activation function ! 
        self.activation = torch.nn.Sigmoid()
        # self.activation = torch.nn.ReLU()


        self.last_activation = torch.nn.Softmax(dim=1)

        # First difference we don't need a special Input layer 😃
        # Second one we can declare them more easely
        for i in range(1,len(config)):
          layer = nn.Linear(config[i-1], config[i])
          self.layers.append(layer)
          self.layers.append(self.activation)

        self.layers[-1]= self.last_activation
        self.model = nn.Sequential(*self.layers)

        # We use the built-in function to compute the loss
        # TODO: Maybe try with another loss function ! 
        self.loss_function = torch.nn.MSELoss()
        # self.loss_function = torch.nn.CrossEntropyLoss()

        # We use the built-in function to update the model weights
        self.optimizer = optim.SGD(self.model.parameters(), lr=self.learning_rate, momentum=self.momentum)

    # Here we see the power of Pytorch
    # The forward is just giving the input to our model
    def forward(self, input_tensor: torch.Tensor) -> torch.Tensor:
      y_pred = self.model(input_tensor)
      return y_pred

    def compute_loss(self, y_pred: torch.Tensor, y_true) -> torch.Tensor:
        y_true = torch.argmax(y_true, dim=1)
        loss = self.loss_function(y_pred.float(), y_true)
        # looking at what the loss looks like
        # print(loss)
        return loss

    # Even more powerful no need to code all the derivative of the different function
    def backward_pass(self, loss: torch.tensor) -> None:
        loss.backward()
        return

    # The previoulsy hard function to update the weight become also easy
    def update_all_weights(self):
      # Using pytorch
      self.optimizer.step()


    def get_error(self, y_pred, y_true) -> float:
      y_pred = torch.argmax(y_pred, dim=1)
      y_true = torch.argmax(y_true, dim=1)
      return (y_pred == y_true).float().mean()

    def get_test_error(self, X_test, y_test) -> float:
      nbatch = X_test.shape[0]
      error_sum = 0.0
      for i in range(0, nbatch):
          X_batch = X_test[i,:,:].reshape(self.minibatch_size, -1)
          y_batch = y_test[i,:,:].reshape(self.minibatch_size, -1)
          y_pred = self.model(X_batch)
          error_sum += self.get_error(y_pred, y_batch)
      return error_sum / nbatch

    def train(self, n_epochs: int, X_train: torch.Tensor, y_train: torch.Tensor, X_test: torch.Tensor, y_test: torch.Tensor):
      X_train = X_train.reshape(-1, self.minibatch_size, 784).to(self.device)
      y_train = y_train.reshape(-1, self.minibatch_size, 10).to(self.device)

      X_test = X_test.reshape(-1, self.minibatch_size, 784).to(self.device)
      y_test = y_test.reshape(-1, self.minibatch_size, 10).to(self.device)

      
      self.model = self.model.to(device)
      nbatch = X_train.shape[0]
      error_test = 0.0
      for epoch in range(n_epochs): 
        error_sum_train = 0.0
        for i in range(0, nbatch):
          X_batch = X_train[i,:, :]
          y_batch = y_train[i,:, :]
          # In order to have the correct derivative we remove the one from before 
          self.optimizer.zero_grad()
          # Then we do a pass forward 
          y_pred = self.model(X_batch)
          # We compute the loss 
          loss = self.compute_loss(y_pred, y_batch)
          # And calculate the backward pass
          self.backward_pass(loss=loss)
          # To finally update the weights using stochastic gradient descent 
          self.update_all_weights()
          error_sum_train += self.get_error(y_pred, y_batch)
        error_test = self.get_test_error(X_test, y_test)
        
        print(f"Training Loss: {loss:.3f}, Training accuracy: {error_sum_train / nbatch:.3f}, Test accuracy: {error_test:.3f}")
      return loss, error_test

if __name__ == "__main__":
    minibatch_size = 28
    nepoch = 50
    learning_rate = 0.1
    ffnn = FFNN(config=[784, 256, 128, 10], device=device, minibatch_size=minibatch_size, learning_rate=learning_rate)
    print(ffnn)
    loss, err = ffnn.train(nepoch, X_train, y_train, X_test, y_test)

"""In pytorch a very convinient way to load data in batch si to use the data loader. 

Let's update the class to use it, we are also going to use dataset available in pytorch vision.
"""

class FFNNModel(nn.Module):
    def __init__(self, classes=10):
        super().__init__()
        # not the best model...
        self.l1 = torch.nn.Linear(784, 256)
        self.l2 = torch.nn.Linear(256, 128)
        self.l3 = torch.nn.Linear(128, classes)
        self.activation = torch.nn.ReLU()
        self.last_activation = torch.nn.Softmax(dim=1)

    def forward(self, input):
        input = input.reshape(input.size(0), -1)
        x = self.l1(input)
        x = self.activation(x)
        x = self.l2(x)
        x = self.activation(x)
        x = self.l3(x)
        y = self.last_activation(x)
        return y

def train_one_epoch(model, device, data_loader, optimizer):
    train_loss = 0
    correct = 0
    for num, (data, target) in tq.tqdm(enumerate(data_loader), total=len(data_loader.dataset)/data_loader.batch_size):
        data, target = data.to(device), target.to(device)
        optimizer.zero_grad()
        output = model(data)

        loss = F.cross_entropy(output, target)
        loss.backward()
        train_loss += loss.item()
        optimizer.step()

        prediction = output.argmax(dim=1)
        correct += torch.sum(prediction.eq(target)).item()

    result = {'loss': train_loss / len(data_loader.dataset),
              'accuracy': correct / len(data_loader.dataset)
              }
    return result   
 
def evaluation(model, device, data_loader):
    eval_loss = 0
    correct = 0

    for num, (data, target) in tq.tqdm(enumerate(data_loader), total=len(data_loader.dataset)/data_loader.batch_size):
        data, target = data.to(device), target.to(device)
        output = model(data)
        eval_loss += F.cross_entropy(output, target).item()
        prediction = output.argmax(dim=1)
        correct += torch.sum(prediction.eq(target)).item()
    result = {'loss': eval_loss / len(data_loader.dataset),
              'accuracy': correct / len(data_loader.dataset)
              }
    return result

if __name__ == "__main__":
    
    # Network Hyperparameters 
    minibatch_size = 28
    nepoch = 10
    learning_rate = 0.1
    momentum = 0 
    model = FFNNModel()
    model.to(device)
    optimizer = optim.SGD(model.parameters(), lr=learning_rate, momentum=momentum)

    # Retrieve the data with the pytorch dataloader 
    mnist_train = MNIST(os.getcwd(), train=True, download=True, transform=transforms.ToTensor())
    mnist_train = DataLoader(mnist_train, batch_size=32, num_workers=4, pin_memory=True)
    mnist_val = MNIST(os.getcwd(), train=False, download=True, transform=transforms.ToTensor())
    mnist_val = DataLoader(mnist_val, batch_size=32, num_workers=4,  pin_memory=True)

    # Train for an number of epoch 
    for epoch in range(nepoch):
      print(f"training Epoch: {epoch}")
      if epoch > 0:
        train_result = train_one_epoch(model, device, mnist_train, optimizer)
        print(f"Result Training dataset {train_result}")

      eval_result = evaluation(model, device, mnist_val)
      print(f"Result Test dataset {eval_result}")

"""# Part 1: What is a convolution ?

In this section you will implement 2D convolution operation using:

Starting with a simple example and manual computation like in Lecture 2

1) Introduction: manual computation

- you have as input an image of 5x5 pixels

$I = \begin{bmatrix}I_{1, 1} & ... & I_{1, 5} \\ \vdots & \ddots & \vdots \\ I_{5, 1}& ... & I_{5,5}\end{bmatrix}$

Your task is to compute the result of a convolution operation between this image and a 3x3 kernel

$ K = \begin{bmatrix}a & b & c \\d & e & f \\ g& h& i\end{bmatrix}$

We are considering padding with 0 and using the SAME convolution. 
Meaning that arround the I matrix consider there is the value 0.

Tips: the result of the convolution is a 5x5 matrix
"""

I = np.array([[252,  49, 113,  11, 137],
                [ 18, 237, 163, 119,  53],
                [ 90,  89, 178,  75, 247],
                [209, 216,  48, 135, 232],
                [229, 53, 107, 106, 222]])
print(f"I =")
print(I)

K_0 = np.array([[0, 1, 0], [0, 0, 0], [0, 0, 0]])
print(f"K_0 =")
print(K_0)

K_1 = np.array([[1, 1, 1], [0, 5, 0], [-1, -1, -1]])
print(f"K_1 =")
print(K_1)

"""What is the result of convolution of $ I_0 \ast K_0 $"""

# put your answer here
R_0 = np.array([[0,  0, 0,  0, 0],
                [252,  49, 113,  11, 137],
                [ 18, 237, 163, 119,  53],
                [ 90,  89, 178,  75, 247],
                [209, 216,  48, 135, 232],])

"""What is the result of convolution of $ I_0 \ast K_1 $"""

# put your answer here
R_1 = np.array([[1005,  -173, 46, -280,513],
                [212, 1242, 646, 356, 91],
                [280,  390, 1010,  295, 1040],
                [942,  1048, 316,  740, 1154],
                [1570,  738, 934,  945, 1477],])

"""## 2) Computation using __numpy__

Now using the numpy implement the convolution operation.
"""

def convolution_forward_numpy(image, kernel):
  (n,m)=np.shape(image)
  mat_sortie = np.zeros((n,m))
  (n,m)=n+2,m+2
  Y= np.zeros((n,m))
  mattrice=np.zeros((n,m))
  py = (kernel.shape[0]-1)//2
  px = (kernel.shape[1]-1)//2
  imax =n-px
  for k in range(0,n-2):
    mattrice[k+1,1:m-1]=image[k]
  for i in range(px,imax):
    for j in range(py,n-py):
      somme = 0
      for k in range(-px,px+1):
        for l in range(-py,py+1):
          somme += mattrice[j+l][i+k]*kernel[l+py][k+px]
      Y[j][i] =somme 
  for k in range(0,n-2):
    mat_sortie[k]=Y[k+1,1:m-1]
  return mat_sortie

mat=convolution_forward_numpy(I,K_1)
print(mat)

"""Test your implementation on the two previous example and compare the results to the result manually computed."""

assert convolution_forward_numpy(I, K_0).all() == R_0.all() 
assert convolution_forward_numpy(I, K_1).all() == R_1.all()

"""Display the result image of the convolution"""

# Load image from url, you can use an other image if you want
image_url = "https://upload.wikimedia.org/wikipedia/commons/4/4f/ECE_Paris_Lyon.jpg"
image = imageio.imread(image_url)


# simple function to display image
def display_image(img):
    plt.imshow(img)

# display the image
display_image(image)


# Do the convolution operation and display the resulting image

(n,m,p) = np.shape(image)
output_image =np.zeros((n,m,p)) 
for i in range(0,p):
  img = np.zeros((n,m))
  img = image[:,:,i]
  output_image[:,:,i]=convolution_forward_numpy(img, K_0)

#output_image = convolution_forward_numpy(image, K_0) 
display_image(output_image)

"""## 3) Computation using __pytorch__

Now let's use pytorch convolution layer to do the forward pass. Use the documentation available at: https://pytorch.org/docs/stable/nn.html
"""

def convolution_forward_torch(image, kernel):
  n,m = np.shape(I)
  M = torch.ones(1, 1, n,m)
  for i in range(0,n):
    M[0,0,i,:]=torch.from_numpy(I[i,:])
  output = nn.Conv2d(1,1,3,padding=(1,1),stride=(1,1),dilation=(1,1),groups=1)
  return output(M)
  
mat = convolution_forward_torch(I,K_0)
print(mat)

"""In pytorch you can also access other layer like convolution2D, pooling layers, for example in the following cell use the __torch.nn.MaxPool2d__ to redduce the image size."""

# pool of square window of size=3, stride=2
ma = nn.MaxPool2d(3, stride=1)
# pool of non-square window
n,m = np.shape(I)
M = torch.ones(1, 1, n,m)
for i in range(0,n):
  M[0,0,i,:]=torch.from_numpy(I[i,:])
#m = nn.MaxPool2d((3, 2), stride=(2, 1))
input = torch.randn(20, 16, 50, 32)
output = ma(M)
print(output)

"""# Part 2: Using convolution neural network to recognize digits

In this section you will implement 2D convolution neural network and train it on fashion mnist dataset

https://github.com/zalandoresearch/fashion-mnist


![Image of fashion mnist](https://raw.githubusercontent.com/zalandoresearch/fashion-mnist/master/doc/img/fashion-mnist-sprite.png)

##  First let's look at the data.
"""

if __name__ == "__main__" :

  fmnist_train = FashionMNIST(os.getcwd(), train=True, download=True, transform=transforms.ToTensor())
  fmnist_train = DataLoader(fmnist_train, batch_size=32, num_workers=4, pin_memory=True)
  fmnist_val = FashionMNIST(os.getcwd(), train=False, download=True, transform=transforms.ToTensor())
  fmnist_val = DataLoader(fmnist_val, batch_size=32, num_workers=4,  pin_memory=True)

#petit test
fmnist_train.dataset.data
display_image(fmnist_train.dataset.data[9,:,:])

"""Display the 10 image from train set and 10 images from validation set, print their ground truth"""

def display_10_images(dataset):
  for i in range(0,10):
    plt.figure(i)
    display_image(dataset.data[i,:,:])

#image from train
display_10_images(fmnist_train.dataset)

#image from validation
display_10_images(fmnist_val.dataset)

#Shape of each image
print(np.shape(fmnist_train.dataset.data[0,:,:]))

# les différentes classes
fmnist_train.dataset.classes

"""What is the shape of each images
How many images do we have
What are the different classes
"""

def fashion_mnist_dataset_answer():
    shape = [28,28]  # replace None with the value you found
    number_of_images_in_train_set = np.shape(fmnist_train.dataset.data)[0]
    number_of_images_in_test_set = np.shape(fmnist_val.dataset.data)[0]
    number_of_classes = np.shape(fmnist_train.dataset.classes)[0]
    return {'shape': shape, 'nb_in_train_set': number_of_images_in_train_set, 'nb_in_test_set': number_of_images_in_test_set, 'number_of_classes': number_of_classes}

# Plot an image and the target  
display_image(fmnist_train.dataset.data[8,:,:])
fmnist_train.dataset.targets[8]
# la position 5 correspond à la classe sandale ce qui correspond à l'image affichée

"""## Create a convolutional neural network

Now it's your turn to create a convolutional neural network and to train your model on the fashion mnist dataset.

Classical machine learning approach manage to get a 89% accuracy on fashion mnist, your objective is to use deep learning (and convolution neural network) to get more than 90%

You can first start with this simple convolution network and improve it by adding/modifying the layers used:

```
convolutional layer 3x3
convolutional layer 3x3
max-pooling
convolutional layer 3x3
convolutional layer 3x3
max-pooling
flatten
fully-connected layer (dense layer)
fully-connected layer (dense layer)
fully-connected layer (dense layer)
Softmax
```
"""

class CNNModel(nn.Module):
    def __init__(self, classes=10):
        super().__init__()
        # YOUR CODE HERE 
        #couche
        self.layer_1 = nn.Sequential(nn.Conv2d(1,32,kernel_size=5,stride=1,padding=2),nn.ReLU(),nn.MaxPool2d(kernel_size=2, stride=2))
        self.layer_2 = nn.Sequential(nn.Conv2d(32,64,kernel_size=5,stride=1,padding=2),nn.ReLU(),nn.MaxPool2d(kernel_size=2, stride=2))
        
        self.Dropout= nn.Dropout(0.25)
        # je peux utiliser self.flatten = nn.Flatten() ou bien x.view(x.size(0), -1)
        self.fcl_1 =nn.Linear(7*7*64,1000)
        self.fcl_2 =nn.Linear(1000,10)
        self.last_activation = torch.nn.Softmax(dim=1)
      

    def forward(self, input):
        x =  self.layer_1(input)
        x =  self.layer_2(x)
        x =  x.view(x.size(0), -1)
        x = self.Dropout(x)
        x =  self.fcl_1(x)
        y =  self.fcl_2(x)
        # YOUR CODE HERE 
        #y = self.last_activation(x)
        return y

def train_one_epoch(model, device, data_loader, optimizer):
    train_loss = 0
    correct = 0
    for num, (data, target) in tq.tqdm(enumerate(data_loader), total=len(data_loader.dataset)/data_loader.batch_size):
        data, target = data.to(device), target.to(device)
        optimizer.zero_grad()
        output = model(data)

        # YOUR CODE HERE 
        loss =  F.cross_entropy(output, target)
        loss.backward()
        train_loss += loss.item()
        optimizer.step()

        prediction = output.argmax(dim=1)
        correct += torch.sum(prediction.eq(target)).item()

    result = {'loss': train_loss / len(data_loader.dataset),
              'accuracy': correct / len(data_loader.dataset)
              }
    return result   
 
def evaluation(model, device, data_loader):
    eval_loss = 0
    correct = 0

    for num, (data, target) in tq.tqdm(enumerate(data_loader), total=len(data_loader.dataset)/data_loader.batch_size):
        data, target = data.to(device), target.to(device)
        output = model(data)
        # YOUR CODE HERE 
        eval_loss += target.size(0)
        prediction = output.argmax(dim=1)
        correct += torch.sum(prediction.eq(target)).item()
    result = {'loss': eval_loss / len(data_loader.dataset),
              'accuracy': correct / len(data_loader.dataset)
              }
    return result
    
if __name__ == "__main__":
    
    # Network Hyperparameters 
    # YOUR CODE HERE 
    minibatch_size = 100
    nepoch = 12
    learning_rate = 0.001
    momentum = 0


    model = CNNModel()
    model.to(device)

    # YOUR CODE HERE 
    optimizer = torch.optim.Adam(model.parameters(),lr=learning_rate)

    # Train for an number of epoch 
    for epoch in range(nepoch):
      print(f"training Epoch: {epoch}")
      if epoch > 0:
        train_result = train_one_epoch(model, device, mnist_train, optimizer)
        print(f"Result Training dataset {train_result}")

      eval_result = evaluation(model, device, mnist_val)
      print(f"Result Test dataset {eval_result}")

np.shape(mnist_train.dataset.classes)

"""## Open Analysis
Same as TP 1 please write a short description of your experiment

En étape 1 j'ai décidé de créer un modèle:

Au départ j'étais partie sur la création de 3 layers; pour chacune d'entre elles j'avais choisi d'utiliser le sequençage.Ce qui me permettait d'effectuer une liste des actions à effectuer pour chacune d'entre elles.
Ce séquençage était le suivant soit on fait une convolution, puis on utilise la fonction d'activation reLU qui remplace toutes les valeurs négatives reçues en entrée par des zéros et donc rend l'ensemble non linéaire.
Après cela, on utilise l'opération max pooling qui va réduire la taille des images de ce fait on passe d'une image de 28x28 à 14x14 grâce au stride de 2.
Ayant fait 3 layers, la réduction totale devait être de 3x3 mais je me suis rendue compte que en réduisant autant mes résultats n'étaient pas intéressant.
De ce fait je me suis arrétée au nombre de deux layers ce qui faisait une réduction de 7x7.

Ma première couche prenait une entrée et donnait 32 sorties; la seconde couche prenait 32 entrées et rendaient 64 sorties.C'est à dire que j'ai augmenté mon nombre de filtres et donc cela permet de cibler encore plus d'informations.
A la suite des opérations effectuées sur les deux layers, j'ai décidé de transformer ma sortie de "64 channels" en un vecteur soit de: 64*7*7=3136 Lignes.
Afin d'éviter un over-fitting je fais un dropout de 0.25.
En dernière partie je crée deux layer fully connected dont la première formera un vecteur de 3136 lignes et le second de 1000 lignes.

J'ai tenté de modifier le momentum pour voir le comportement du systeme et lorsque je passe une valeur de 0.8 l accuracy diminue fortement de ce fait j ai décidé de le mettre à nul.J'ai également remarqué que le fait d'augmenter le nombre d'epochs ne changeait rien à mon accuracy c'est à dire que au delà de 10 j'ai des oscillations de valeurs.

Par rapport au tp précédent j'avais remarqué qu'un learning rate très faible impliquait des valeurs d'accuracy faibles dû à l'update des poids.Ainsi j'ai décidé de prendre un learning rate de 0.01.
J'obtenais alors des valeurs d'accuracy qui vascillaient entre [0.86 et 0.90],
la probabilité d'obtenir une accuracy supérieure à 0.90 était assez faible.
J'ai donc décidé de faire quand même des tests avec un learning rate plus faible soit 0.001 et là je fus très surprise par le résultat!!!
J'obtenais des valeurs d'accuracy qui vascillaient entre [0.97 et 0.99].

Ainsi en conclusion je me suis rendue compte que contrairement au tp 1, le learning rate doit être très faible.

# BONUS 

Use some already trained CNN to segment YOUR image. 

In the cell below your can load a image to the notebook and use the given network to have the segmentation mask and plot it.
"""

if __name__ == "__main__" :
    
    # TODO HERE: Upload an image to the notebook in the navigation bar on the left
    # `File` `Load File`and load an image to the notebook. 
    
    filename = "chaton.jfif" 
    # Loading a already trained network in pytorch 
    model = torch.hub.load('pytorch/vision:v0.6.0', 'deeplabv3_resnet101', pretrained=True)
    model.eval()

    from PIL import Image
    from torchvision import transforms

    input_image = Image.open(filename)
    preprocess = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

    input_tensor = preprocess(input_image)
    input_batch = input_tensor.unsqueeze(0) # create a mini-batch as expected by the model

    # move the input and model to GPU for speed if available
    if torch.cuda.is_available():
        input_batch = input_batch.to('cuda')
        model.to('cuda')

    with torch.no_grad():
        output = model(input_batch)['out'][0]
    output_predictions = output.argmax(0)

