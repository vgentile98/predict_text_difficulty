# Madame Toast's French Adventure

![bannière 1](image/bannière_1.png)



## 1. Why? - Our Challenge

Madame Toast, a British toast, has always had a taste for adventure and challenge. From her London kitchen, she dreams of strolling the cobbled streets of Paris, picking up croissants, chatting to the finest macaroons and reading French classics with ease. But to do so, she has to overcome a major obstacle: learning French.

### 1.1 Context
This project was carried out as part of the ‘Data Science and Machine Learning’ course given by Professor Vlachos in the SMT master's programme. The idea for this project arose from a Kaggle competition aimed at improving foreign language learning.
The aim of the Kaggle competition was to create a model capable of predicting the difficulty of texts written in French for English speakers. 

For Madame Toast, the problem is clear: it is often difficult to find texts that perfectly match her level of proficiency, ranging from A1 to C2. An ideal text should contain a mix of familiar and unfamiliar words, to allow for a natural and stimulating progression. 

### 1.2 Pedagogical Importance 📘
Madame Toast has a clear pedagogical principle: free and voluntary reading. As Krashen (2004) points out, this method allows students to choose reading material that interests them personally. This encourages them to read more and acquire new words in relevant contexts.
However, Madame Toast is a new-generation toast and doesn't stop at written texts. She also loves videos. Martínez (2022) highlights the benefits of YouTube videos, including their accessibility, diversity of topics and levels of difficulty, and their ability to provide practical examples for specific skills, such as pronunciation. These resources are essential for Madame Toast, as they provide her with varied and practical opportunities to improve her French.

### 1.3 Our goal 🎯
Our goal is clear: to help Madame Toast determine the difficulty of texts so that she can read those that are adapted to her level, and to measure the progress of her comprehension by gradually confronting more complex texts. Madame Toast will meet Monsieur Baguette, the most intelligent baguette in France, who will use his innovative application to help her analyze and predict the level of French sentences. This will facilitate personalized and progressive learning, making the process of learning French more motivating.
For Madame Toast, every word she learns is a victory, every sentence she understands is another step towards mastering the language. She set off from London ready to overcome every obstacle on her way to understanding French. Her journey begins, with Paris as her final destination, where she hopes one day to converse fluently with Parisian brioches and read the works of the famous poet Victor Baguetto.

<p align="center">
  <img src="image/Victor_Baguetto.png" alt="Victor Baguetto" width="200"/>
  <br>
  <em>Victor Baguetto, the famous poetic baguette</em>
</p>

## 2. How? - Our Methodology

![bannière 2](image/bannière_2.png)


### 2.1 Exporing Models 🔢
To start our project, we established baseline models to serve as a reference for future improvements. Our baseline models use simple algorithms and default parameters to provide an initial performance benchmark. After establishing our baseline models, we conducted hyperparameter optimization to improve their performance. Hyperparameter optimization involved the following steps:

1. **Defining Parameter Grid**: Specifying a range of values for each hyperparameter. For example, for Logistic Regression, we varied the regularization strength and the solver type.
2. **Search Method**: Using Grid Search and Random Search to explore different hyperparameter combinations systematically.
3. **Cross-Validation**: Evaluating the performance of each combination using 5-fold cross-validation to ensure the model generalizes well.
4. **Selecting Best Parameters**: Identifying and selecting the combination that yields the best performance metrics.

We then retrained the models using these optimized settings to ensure they were fine-tuned for optimal performance. After retraining the models with the optimized hyperparameters, we evaluated their performance on the test data. The report table below shows the precision, recall, F1-score, and accuracy for all the optimized models:

<p align="center">
  <img src="image/models_table.png" alt="Comparison Table" height="300"/>
  <br>
  <em>Models Performance Comparison</em>
</p>

From our report table, models can be categorized by their performance:
- **Best Model**: The Neural Network model outperforms all other models in terms of precision, recall, F1-score, and accuracy. This indicates that it is the most effective model for this classification task.

- **Poor Performers**: KNN and Decision Tree show the poorest performance, struggling to classify the text difficulty accurately.

- **Moderate Performers**: Logistic Regression, Random Forest, and Gradient Boosting have moderate performance, with balanced but not outstanding metrics.

- **Good Performers**: SVM and Naive Bayes perform well, with good precision, recall, F1-score, and accuracy, but are slightly outperformed by the Neural Network.

Therefore, our neural network model is the focus of our further analysis and improvement steps. In the next sections, we take a closer look at this best model, analyze its performance in more detail, and refine it to achieve even better results.

### 2.2 Analyzing & Improving The Best-Performing Model 🧠
#### 2.2.1 Confusion Matrix

<p align="center">
  <img src="image/confusion_matrix_nn.png" alt="Confusion Matrix" height="350"/>
  <br>
  <em>Confusion Matrix</em>
</p>

Out of the confusion matrix of our neural network model, here are our key observations:
- **Strong Performance for A1 and B1**: The model performs well in predicting A1 and B1, with 96 and 91 correct predictions, respectively.
- **Moderate Performance for A2 and C2**: The model has a moderate number of correct predictions for A2 (69) and C2 (90). However, there are still significant misclassifications in these categories.
- **Confusion Among Intermediate Levels (A2, B1, B2, C1)**: There is noticeable confusion among the intermediate levels (A2, B1, B2, C1). For example, B1 is often misclassified as A2 (35 times) and B2 (26 times).
- **Challenges with B2 and C1**: The model struggles more with B2 and C1, showing lower correct predictions (66 for B2 and 65 for C1) and higher misclassifications across other levels.

Therefore, two key insights drive our next improvement actions:
- The model's ability to distinguish between adjacent levels (e.g., A1 vs A2, B1 vs B2) could be improved.
- There are relatively fewer misclassifications between non-adjacent levels (e.g., A1 to C2), which indicates the model understands the general progression of difficulty but has trouble with finer distinctions.

#### 2.2.2 Erroneous Predictions

<p align="center">
  <img src="image/erroneous_examples.png" alt="Erroneous Classifications" height="250"/>
  <br>
  <em>Erroneous Classifications</em>
</p>

Diving deeper into these concrete examples of misclassification, here are our key observations:

- **Complex sentences with higher difficulty**: Sentences labeled as C2 are often misclassified as C1 (e.g., "J'étais également incapable de distraction et d'étude."). This might be due to subtle nuances and complex structures in C2 sentences that are not captured effectively by the model.
- **Intermediate levels**: As previously observed already, misclassifications are common among intermediate levels (e.g., B1, B2, C1). For instance, "Elle est arrivée blessée à la consultation médicale, mais souriante." is labeled as B2 but predicted as B1. This indicates that the model struggles to differentiate between closely related difficulty levels.
- **Simple sentences misclassified as harder levels**: Simple sentences like "Ils sont au lycée français." labeled as A1 are misclassified as B2. This suggests that the model may be overestimating the complexity due to certain keywords or structures.
- **Contextual ambiguities**: Sentences with contextual ambiguities or idiomatic expressions (e.g., "Il la sentait contre lui, si près, enfermée avec lui dans cette boîte noire...") are challenging for the model, leading to misclassifications. These cases probably need more contextual understanding which might not be fully captured by our baseline model.

#### 2.2.3 Further Behaviour Analysis

Let's do some more analysis to better understand how our model behaves.

<p align="center">
  <img src="image/misclassification_per_label.png" alt="Distribution Across Classes" height="250"/>
  <br>
  <em>Distribution of Misclassifications Across Classes</em>
</p>

The misclassification rates across different classes reveal that:

- **High Misclassification Rates for A2, B2, and C1**: These classes exhibit the highest misclassification rates, indicating that the model finds it particularly challenging to distinguish texts within these categories.
- **Lower Misclassification Rates for A1 and B1**: These classes have relatively lower misclassification rates, suggesting better model performance for texts at these difficulty levels.
- **Intermediate Levels**: The intermediate levels (A2, B2, C1) continue to pose significant challenges for the model, confirming our earlier observations from the confusion matrix.

These findings suggest that the model **struggles with finer distinctions between difficulty levels, especially among intermediate classes**.

<p align="center">
  <img src="image/misclassification_patterns.png" alt="Common Misclassification Patterns" width="250"/>
  <br>
  <em>Common Misclassification Patterns</em>
</p>

The table of common misclassification patterns reveals that:

- **Adjacent Levels**: The most frequent misclassifications occur between adjacent levels (e.g., A1 misclassified as A2, A2 misclassified as B1). This indicates that the model has difficulty differentiating between closely related difficulty levels.
- **Patterns of Confusion**: There are specific patterns of confusion, such as A1 and A2, and B1 and B2, where misclassifications are most common.
  
These patterns highlight the need for improved **feature extraction or additional context to better differentiate between similar difficulty levels**.

<p align="center">
  <img src="image/sentence_length_effect.png" alt="Effect of Sentence Length on Misclassification" height="250"/>
  <br>
  <em>Effect of Sentence Length on Misclassification</em>
</p>

The analysis of sentence length distribution indicates that:

- **Shorter Sentences**: Misclassified instances tend to have shorter sentences compared to the overall distribution. This suggests that shorter sentences may lack sufficient contextual information for accurate classification.
- **Longer Sentences**: There is a slight overlap in the distribution of sentence lengths for correctly classified and misclassified instances, but shorter sentences are more prone to errors.

This insight implies that **enhancing the model's capability to understand context in shorter sentences could improve overall accuracy**.

### 2.3 Final CamemBERT Model 🧀

#### 2.3.1 How Does the Model Determine Difficulty?
Our final model determines the difficulty of French texts using a fine-tuned CamemBERT model. CamemBERT is a transformer-based model specifically designed for French language understanding, similar to BERT but adapted to French. The model takes in text inputs and processes them to predict the difficulty level based on the learned patterns from the training data.

#### 2.3.2 What Does the Algorithm Include?
**Data Preparation**:
- **Text Preprocessing**: Clean the text data by converting to lowercase, removing punctuation, and removing extra whitespace.
- **Label Encoding**: Encode the difficulty levels into numerical format for training.

**Data Augmentation**:
- **Augment the training data**: Use synonym replacement to increase the diversity of training examples.

**Tokenization and Encoding**:
- **Use the CamemBERT tokenizer** to convert text into tokens and encode them into input tensors suitable for the CamemBERT model. This involves adding special tokens, truncating to the maximum length, and generating attention masks.

**Model Training**:
- **Load the pre-trained CamemBERT model and fine-tune it** on the training data.
- **Apply class weights** to handle class imbalance during training.
- **Use dynamic padding** to efficiently handle varying sentence lengths.

**Optimization**:
- **Use an AdamW optimizer with a learning rate scheduler** to adjust the learning rate during training.
- **Apply exponential decay** to stabilize training.

#### 2.3.3 What Key Improvements Have Been Made?
Compared to our baseline neural network model, our fine-tuned CamemBERT model offers several enhancements. It provides a deeper and more nuanced understanding of French, thanks to the advanced pre-trained language model. Dynamic padding efficiently handles variable-length inputs, while advanced learning rate scheduling and exponential decay improve training stability. Augmenting the data with synonym replacement increases dataset diversity and robustness. Additionally, class weights are used to address class imbalance, ensuring better performance across all difficulty levels.

#### 2.3.3 Model Evaluation
Here is a summary of our results, which show the performance of the fine-tuned CamemBERT model on the validation set:
<p align="center">
  <img src="image/camembert_evaluation.png" alt="Final Model Evaluation" height="250"/>
  <br>
  <em>Final Model Evaluation</em>
</p>

**Training Performance**:
- The training loss consistently decreases across epochs, indicating that the model is learning from the training data effectively.

**Validation Performance**:
- The validation metrics (accuracy, precision, recall, F1-score) improve over the initial epochs, reaching the highest values around epochs 3 to 5.
- There is a slight drop in performance in the final epoch (epoch 6), which could indicate some overfitting or fluctuations in the learning process.

**General Performance**:
- The CamemBERT model achieves a peak validation accuracy of 66%, precision of 69%, recall of 66%, and F1-score of 67% around epoch 3.
- The final metrics are slightly lower but still demonstrate decent performance with 63% accuracy, precision, recall, and F1-score.
  
With this model, our accuracy on the actual test data was 0.602, which ranked us **14th** in the Kaggle competition.

### 2.4 OpenAI Fine-tuning
As a final step, Mr Baguette tried model fine-tuning. This is a case of transfer learning where an existing model is trained on a specific task in order to optimise its performance. We used OpenAI models, for which you can obtain your API key and all the documentation on their dedicated platform: [OpenAI Platform](https://platform.openai.com/docs/overview)

**Fine-tuning steps**

**1. Data Preparation:** Gather and prepare the data specific to the task for which you wish to fine-tune the model. For ‘davinci 002’, the data must be organised into prompt-response pairs.

**2. Model Selection:** Choose a pre-trained base model such as ‘davinci 002’ or ‘gpt-3.5-turbo’ from the OpenAI platform.

**3. Model Training:** Use the OpenAI API to start the fine-tuning process with your prepared dataset.

**4. Evaluation and Prediction Generation:** Evaluate the performance of the fine-tuned model. Make predictions on test data. 

We found slightly lower results in terms of accuracy compared with our best Bert model, but better consistency in the results. The model that works best is ‘davinci 002’, followed by the famous ‘gpt-3.5-turbo’.

To obtain our best results, we used a temperature of 0.2 and a seed of 42 when generating the predictions. You will find a notebook to use in the document. You will of course need to enter your own API key for this to work. The notebook shows an example of fine-tuning the ‘davinci 002’ model.

**Data format**
For the ‘davinci 002’ model, the training data must be organised in JSON format with prompt-response pairs as follows:


{"prompt": "Bonjour, comment ça va ?'",
  "completion": "A1"}

To use the ‘gpt-3.5-turbo’ model, the data must be organised in a different format, following the structure below:


{"messages": [
    { "role": "system", "content": "You class French text on their difficulty" },
    { "role": "user", "content": "Bonjour, je suis une baguette'" },
    { "role": "assistant", "content": "A1" }
  ]}

By following these steps and using the appropriate data formats, you can, like Mr Baguette, fine-tune the OpenAI models to classify the level of French text. 


![bannière 3](image/bannière_3.png)
## 3. What? - Our Solution

Now that we've found the right model for Madame Toast to overcome her major difficulty of defining the difficulty of texts, she only needs to take a few more steps before conquering Paris. When she arrived on French shores, she met Monsieur Baguette. An experienced StreamLit application developer and madly in love with Madame Toast, he decided to develop an application that would meet her needs perfectly.

The fundamental educational principles he has implemented in the application include free reading and different types of media, gamification, progress tracking and adaptation to the user's level.

<div align="center">
    <a href="https://www.youtube.com/watch?v=pcwYBXNNm6E" target="_blank">
        <img src="image/video.png" alt="Tutoriel YouTube" width="500"/>
    </a>
</div>


The main features of Monsieur Baguette's application are as follows:

### 3.1 Level assessment 🥇
Before starting to learn French, Mr Baguette first had to assess Mrs Toast's current level so that he could offer her suitable texts and videos. Eager to do the right thing, he suggests a questionnaire to assess her level.

### 3.2 Article and Video Browser 📄🎬
Madame Toast can now search for articles and videos by filtering them according to the themes that interest her. This is made possible by the YouTube API for videos and the Media Stack API for articles. Monsieur Baguette's application obviously offers texts and videos that match the user's level. If Madame Toast would like to read the transcript of the video, that's also possible.

### 3.3 Immediate translation 🇬🇧
If Madame Toast doesn't understand a word, she can copy and paste it into the translator in the sidebar to get an immediate translation, thanks to the Google Translate library.

### 3.4 Vocabulary list 🆕
For words she wants to remember, she can add them to her vocabulary list, where she will have the definition thanks to the PyDictionary library, as well as the translation. She can also remove a word when she considers it has been learnt and track the evolution of her vocabulary.

### 3.5 Feedback process 🌟
Each time Madame Toast reads a text, she can give feedback: ‘Too Easy’ , ‘Just Right’ , ‘Challenging’, 'Too Difficult' . Depending on her answers, her level gradually changes and the application recommends texts adapted to her new level. She can also consult all her statistics on a dedicated page showing her progress and the various badges she can acquire as she progresses.

These are the key features of the application that really appealed to Madame Toast. Thanks to her desire to learn and the fact that Mr Baguette's application was perfectly suited to her needs, she is no longer content to just say ‘Oui Oui’ to everything. Monsieur Baguette asked her to go for a drink on a Parisian terrace, but she replied ‘Non Non’ and went off into the arms of Monsieur Croissant, who recited Victor Baguetto's famous verses to her.

![bannière fin](image/bannière_fin.png)

## Literature References

Ma, Guadalupe, Martínez. (2022). YouTube Videos as a Resource for Self-Regulated Pronunciation Practice in EFL Distance Learning Environments. Journal of English language teaching and applied linguistics, 4(2):44-52. doi:10.32996/jeltal.2022.4.2.4:

Krashen, Stephen. (2004). The Power of Reading: Insights from the Research.

