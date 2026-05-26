Summary

### Overview

This is the fourth session focusing on the modeling phase of the CRISP-DM methodology.   The session covers data splitting strategies, baselining, model assessment, and the practical implementation of modeling systems. After several weeks focused on data understanding and preparation, the class is now moving into building and validating models.  

### Core Modeling Concepts

**The 80/20 Rule of Modeling**

- Students often think the work is in choosing algorithms, tuning hyperparameters, or selecting deep vs shallow models
- The real work is in defining the baseline and setting up proper evaluation frameworks
- The model itself falls out at the end of the process, not the process itself
- Structural numbers are meaningless without the load case and safety factor

**Separation of Human vs AI Responsibilities**

- Humans design the split strategy, decide baselines, defend model decisions, and choose appropriate metrics
- AI implements the code (group folds, time series splits, SQL learn pipelines, dummy regressors)
- The key is having defensible systems that you understand and can explain
- In the current age, everyone is becoming an architect/designer rather than just a developer

### Data Splitting Strategies

**Three Dataset Roles**

- **Train**: Where the model learns, can be examined extensively
- **Evaluation**: For tuning and selecting models
- **Test**: End-to-end validation, must produce deterministic answers

**Why Random Splits Don't Work**

- Random splits assume each row is independent, which is almost never true for environmental, spatial, or temporal data
- Creates information leakage through future timestamps, same entities in train/test, or features derived from targets

**Four Split Approaches**

1. **Random Rows**: Assumes independent data points, rarely appropriate for environmental/spatial/temporal data  
2. **Time Series**: Uses date cutoffs, trains on past to test on future   
    - Cannot shuffle data
    - Gets fewer effective folds
    - Good for temporal predictions
    - Example: Train on data before August 1st, evaluate August 1-September 1, test after September 1st
3. **Spatial/Clustered**: Groups data by geographic regions    
    - Holds out entire regions
    - Uses latitude/longitude clustering
    - Good for testing across different cities or areas
    - Example provided clusters data into five groups
4. **Entity/Grouped**: Each entity (building, patient, user, station) is held in one set  
    - Train on stations 1-7, test on stations 8-10 to predict unseen entities
    - Requires large enough datasets to train on most data and predict remainder

**Critical Rule for Test Sets**

- Once the test set parquet is written at split time, you cannot look at it
- The model must be locked in its hyperparameters
- This discipline is commonly missed but essential for valid evaluation

### Baselining

**Purpose and Importance**

- Baseline is the standard that all models are measured against
- Always comes first because it defines what "good" means
- Everything must be compared to this standard

**Types of Baselines**

1. **Dumb Baseline (Mean/Mode)**:  
    - Predicts train mean for regression or most frequent class for classification
    - Represents the floor - model must capture some signal beyond this
    - Like evaluating a Gaussian curve of student test scores
2. **Persistence (Time Series)**: 
    - Uses previous values to predict future
    - Captures signals beyond simple inertia
    - Good for temporal data
3. **Spatial Nearest**: 
    - For spatial data, uses nearest measured point as prediction
    - Captures signals beyond geographic location alone
4. **Domain Heuristics**:  
    - Most useful baseline approach
    - Based on what engineers, planners, or domain experts already know
    - Captures signals beyond existing field knowledge
    - Particularly important given students are working on specific domain problems

**When Baseline Fails**

- If model can't beat baseline, may indicate:
    - Wrong brief/problem formulation
    - System doesn't carry needed information
    - Features don't carry signal
    - Models too weak

### Model Assessment and Metrics

**Problem Types and Approaches**

- Regression, classification, time series, spatial predictions, image sequencing all have different requirements
- Student experience varies: some worked on crowd pattern prediction with images, flood prediction with time series, disaster damage prediction with CMS-AUNAT models

**Practical Guidance**

- Linear models almost always work for typical datasets
- Deep learning needs millions of examples - not appropriate for 5,000 rows with 12 features
- "Boring usually wins" - simple approaches give best results for most projects

**Metrics by Model Type**: 

- **Regression**: Interpretable units, R-squared
- **Balanced classification**: Accuracy metrics
- **Imbalanced classification**: Precision metrics
- **Forecasting**: Time-based evaluation
- **Uncertainty**: Confidence intervals

**Model Cards Must Include**:   

- Training, evaluation, and testing performance
- Baseline metrics chosen
- All splits, models, threads, and segments
- Performance by session/station/class as relevant
- Never report just one headline number

### Documentation Requirements

**Data Sheets**: 

- Document how models work and what they predict
- Must list at least three things model is NOT for
- Examples: "Not for regulatory air quality compliance", "Not for individual health advice", "Not for predictions outside trained spatial extent"
- Sets clear boundaries for appropriate use

**Model Artifacts Should Include**: 

- Weights
- Transforming models
- Prediction chains
- Systems to load from disk and make predictions

### AI Assistance and Current Context

**Speed and Capability**

- Tasks that took weeks two years ago can now be done in 2-3 days with AI assistance
- The class previously spent entire seminars just on modeling systems
- Current cohort will model, train, and build out systems in next 2-3 days

**Industry Trends Discussed**

- Toronto Tech Week happening currently, everyone talking about AI capabilities
- Moving toward day when no one writes code manually
- Problem: People don't understand what they're building
- Analogy: Software developer taking 2-3 weeks instead of 2 days would know where bugs are, unlike someone who built in 2 days with AI but spends weeks debugging

**Key Advantage for Architecture Students**

- Methodology of thinking is the most valuable trait
- Architecture training provides significant advantage in system design
- This seminar focuses on applying architectural thinking methodology to data systems

### Next Steps and Timeline

**Immediate Work** (This session and next):  

- Split the data
- Train models
- Plan model deployment
- Get models ready for use

**Upcoming Sessions** (Next 2-3 sessions): 

- Synthesize data
- Stress test models
- Build UX/UI for model interaction
- Focus on making models actually useful, not just functional

**Constraints for Current Work**: 

- No generating fake data
- No making galleries
- No tuning secondary models (only tune one)
- Focus energy on parameter sweeps
- Baseline must be defensible and worth the effort

### Action Items

- [ ]  All students to push code to GitHub immediately for review by instructor and Salvador
- [ ]  Students encouraged to book sessions with Salvador for additional support
- [ ]  Instructor to upload model files, new materials, and files to GitHub repos
- [ ]  Students to submit MD files including data sheets on model predictions and systems
- [ ]  Students to specify at least three things their models are NOT for
- [ ]  Instructor to test some student models by pulling and evaluating them
- [ ]  Students to work in breakout rooms with instructor visiting each group

### Important Reminders

- Keep the original brief and ICP (Ideal Customer Profile) in mind throughout modeling
- Stay focused on who the end user is and what decisions they need to make
- Understanding your system is more important than implementation details
- Momentum is good - having two sessions this week allows staying engaged without rebuilding momentum

Notes

Transcript

Hello? Hi, hi, hi.

Ya Habibi Bukra Walad ♪ ♪ D.

I need ♪ ♪ A BU  Um... I am the one who created the world And I met the horse Waaahhh, bird.

Amani wa abilta The Dunya I found love Hello?

How's everyone going?

Hello, hello.

I feel like I haven't seen you guys in a month. Two weeks, I think. I don't know.

The gaps are too long. Now we have two sessions in the same week. So, you know, haven't seen you in a month, but I'll see you guys back to back. Amazing. Okay, one second. Let's give it a couple minutes for everyone else to join. Just for two minutes. Yes. transcript What the...

Okay.

I'm getting this set up. I've asked you guys all this many, many times. If any of you has not pushed their code to GitHub for Salvador and I to actually be able to review them, Please do so right now. I'll give you guys a couple minutes. It's very, very, very important that we're actually able to get this beforehand. I don't want to be marking anyone differently. So if anyone can actually be submitting their code, please, to GitHub.

Who has submitted their code?

I think I submitted something.

There is something there.

There's something there to look at, that's for sure.

Okay, I'm going to give you guys a couple minutes just before we get started because I'm waiting for the host... Host thing, can you just please all push your code up for last session? While I just get this set up, just check into your team and see if it's all set up.

She said.

I recommend this fish because I gave it the diet that Raya made for meHey, hey, hey, hey, hey. He's making food and recipes for me Shell bottle. Okay. Let's see. What have we Okay, all right.

You guys ready? Ready. Amazing. Okay. Um, Let me share my screen. You could clean.

You can see the screen, right? Yes, you can. Yep. Amazing. All right.

Alright guys, so we're doing the fourth session today.

We're still part of the four models of CrispDM modeling. This is where basically We're getting into modeling. I hope to God that what we've done so far is we've done all the data preparation properly and went through all those different models. The concept more of what we're going to do here today is we're going to basically look at what it is and how we're going to continue using the data to model and actually look at if the data qualifies to what we're trying to build.

So this is the kind of split that decides what's allowed to actually be able to be used and what's not. All of the data that you prepared, now this is where you validate. make sure that, okay, does it all fit together into one system? So what we have done so far is we just to kind of very iteratively look at it. We've done the data understanding, we've done the data preparation. I know this is a very prolonged way for us to get to a simple goal at the end of it, which is to build the system, but it is very, very important to have the mentality of how we're thinking through to the actual process.

So today we're going to be modeling, which means splitting, baselining, modeling, and assessing how this entire system gets built out. So, From here, I'm going to show you this every single slide in every single session, which is this is the entire model that we're going through. We started in understanding. We looked at exploring the data. We're prepared the data. Today, we actually look at it. Today, we actually build the systems that we said we wanted to build.

Today, we look at how does it all come together to validate the hypothesis for the ICP that we chose. If this actually validates, does this person be able to actually build and actually get to the conclusions for him to actually have a better systems So, we're going to split it up into basically four sections where we're going to be doing a split, which can mean you can be training the data, evaluating the data, testing the data. We are going to baseline it on what the actual bottom of the model looks like for us to actually evaluate it.

And we're going to model what this pipeline looks like for you to actually get benefits from the actual systems that you've decided to actually build. Again, I'm going to upload more folders in each session. You will take a look at them afterwards. I didn't get a chance to upload them yet, but I'll post all of them there. From there, you're actually going to be able to do a bunch of files where you can see here we're basically doing a bunch of modeling for how this information looks like.

Um The point of what I'm trying to say is when we're talking about modeling, we're not me. We don't evaluate that. This is basically the solution. What we're saying is the hypothesis for the data that we're testing. It's more of a structural calculation and not the building. It's the hypothesis about the building. It's validated against loads, the split is the load case, the metric is the safety factor.

It's a great analogy to look at. This is not really the actual answer as much as it's the scaffolding around the buildings of what we're building to evaluate if it fits into the metrics we're trying to make. And that's basically what we're going to spend most of our time doing today, and most of the time with me in each of your sessions. I know that most of these sessions basically kind of take shape in the actual workshop at the end where each of you are split into groups, so that's again where we'll spend most of our time, but this is kind of to set the standard.

The thing that's important here is this is an 80/20 of modeling. It's where students mostly think that the work is. It's choosing the right algorithm. It's choosing the tuning the hyper parameters. It's picking the deep over shallow. It's choosing the model whether it's singular or not. It's where all the actual work is. It's defining the baseline. The model is actually what falls out at the end of the process.

It's not the process itself. And I think that's a very big distinct thing to kind of One of the architectural analogies that I look at as well is if you look at the right hand side, it's the one that I want you to hold. It's structural number is meaningless without the load case and the safety factor. And I think this is a very, very interesting perspective. And I know you guys heard a lot about it.

It's where you kind of attest and split the baseline of how you're actually being able to evaluate the system. So again, we're going to be able to talk about how AI fits into this. And I know I mentioned this a bunch of times about how the distinction between you and the AI. And I think that the entire premise of this entire workshop and seminar is to separate how you interact with AI and how you're actually being able to evaluate how you think rather than how you actually execute.

And a great example, and I want to walk through every single one of them here. the designs and the AI is what builds. So for example, you have, you're deciding the split strategy for the data structure and the AI is writing the group folder, the time series splits code or whatever actual mathematical equations we need to actually evaluate that. You're deciding which baseline the model must beat and the AI is implementing whatever dummy regressor, persistence or spatial means.

You're defending every model in the decision log. You're writing the intents on how you want to use and how you want to limit this actual model. the metric stable of the card. Again, I know that we kind of looked through a bunch of these systems before to evaluate how it's actually going to look like and how we're actually going to be building it. But the point of what I'm trying to say is We're going to continuously walk through these cases where each of these metrics on the side are evaluating how we're actually going to be thinking about the approach and how we're thinking about the solutions. So you're deciding which metrics work for you and your problems and fit the actual problems and data size. And the AI is writing the SQL learn pipelines.

And that's the one that's saving the actual job lips. Like, this is how we're going to be separating these actual systems. Does that make sense? I know we kind of walk through it a lot, but I hope at this point, we're kind of at a point where we understand that this is how we're going to be doing it. to separate the thought process. Yes, thumbs up?

Yeah, yeah, yeah, makes sense. Makes sense for me.

Okay, so first part we're going to talk about is splitting. Okay, this is one of the four phases that exist. It's single highest leverage decision for how you're going to make this all day. It's very important to like not be able to get this wrong because that's what we're going to spend a lot of our time on. And this is now we're going to talk about how we're splitting the data. So, that's going backwards. So there are three sets, there are three roles. First one is train. Where does the model learn?

How are you looking at it? As much as you want. The evaluation is how are you tuning the actual information that you're getting to look at it, but you maybe actually train the model with what you have. Are you using this data to evaluate what model needs to be done? Are you using the data to actually evaluate what you want to build a software? Maybe this is us talking more about us using an AI. you And how does it fit into the tests across this system? And if we are doing that, then we're splitting the data to train the actual model. And this is where we're going to have the most amount of time.

We're going to evaluate and fine-tune it for more than the amount of time that exists here. And then we're going to have it to be tested end-to-end to see what the model is and how it's performing. The most important part about it is that it's iteratively giving you the same deterministic answers. If you're not able to generate deterministic answers against your model, then you have not trained and evaluated them properly.

Okay. So... The next thing I think that's important is that random splits are basically not evaluated as much as we want them to. There's an implicit assumption of SQL learned testing that is the very row that is independent. It's drawing 15% at random. It gives a fair sample of the sample distribution. And that's almost never true, basically. For the data we work with, the data should be deterministic. And I think that's what I continue to talk about. That's why we spent a lot of our time removing anomalies. We spent a lot of our time evaluating if this data actually works or what we're trying to build.

And we're going to be spending most of our time actually to find that each one of these information whether it's hours whether it's actually data metrics for temperatures are identically evaluating what we need to do so if you have for example stations that are 200 meters apart they are that look nearly identical that's also the same building that shows up a dozen times that's also the random split that the randomness is basically not how we choose how we split these answers right And this is basically how we're actually evaluating what that would look like for us.

It's basically a leak of information. And we spent a lot of our time, and I think now we're going to see if the data that we have is suitable enough to be used within the systems we're trying to build. Okay, so... There are basically three ways that we can look at that and I think we mentioned this last time and I think I want to mention this again which is the three ways that the leakage of the information and data that you have can go away is that if you have future timestamps the same entity that you're training and testing if you continue to use the same information to train and train and train and train your data then that information is basically you're building it's not a pattern anymore it's you're building the entire information.

You have Maybe in locations that are in the both sets you have a feature that's basically derived from the target So this is like what we talked about which is like an average PM 2.5, which is this week It's predicting today's PMF and the future is in the column itself And what we're talking about is what are we using for the model itself to continue to predict it outwards and outwards and outwards So from here you basically have four different approaches.

You can either build a time series, you can either build spatial or clustered data, you can either do an entity or grouped way of information, or you could do a random rows, right? And this I think it's genuinely how we're going to consciously per data set justify how we're doing the modeling logs. And the four strategies are very dependent and I want to talk about each one of them. If you're doing random This is genuinely assuming that each rose is an independent data set, which is pretty rare because everything we're testing is continuously in a time series.

But what this would cost us is that exactly like I was saying is that almost never the right call for environmental, spatial or temporal data because they're continuous. So I would not recommend this approach, but it's important to know how does modeling data look like, especially if we're in a situation where we want to evaluate using eval situation. So, and this is basically what we're going to do to start the coding, which I know, for example, I know Rafiki like jumped ahead and did some coding. And this is basically how we're going to evaluate if this is done here for us, which is you have the data.

How am I now going to be testing it? And using the random rows is as one of the approaches that doesn't work for us. If you do time series, which I think is a very, very, very good evaluation for the data set, it has date cutoffs. You can train it on the past and you can also test it on the future. And I think this is a good approach for a lot of the data that we're using. But it's something to keep in mind that you can't really shuffle it around, you get very few effective folds, and there's a big cost for it actually getting honest evaluations. The last two for us of how we want to approach this modeling strategies could be spatial or clustered. Basically, you're trying to group them together within a specific domain, whether that's through a specific access or a specific area.

It basically holds out an entire region. data region for Barcelona and I think that here you get more variances because you are testing different cities that might have completely different answers but again this is a really really good approach for what we're trying to do here. The last approach that we can have is entity which is grouped. And basically, this is us saying that each entity holds a specific fold of data modeling. So that could be, I'm going to test one building as an entity, one patient as an entity, one user, whatever it is, those are different entities that we're grouping them against.

And again, this usually has an unusual mixes of entities within them that kind of maybe skews the data to a specific direction. So this is basically what we're going to do. approach as a data set for modeling. We're going to spend a lot of our time having all the data that we prepared now be modeled to what it looks like to actually evaluate and get these answers. And I think this is probably where it gets a little bit way more exciting because we're no longer in the theory and now we're in the weeds of trying to build this out.

So A good example here, basically, I'm going to continue, guys, just to show you some codes. But this is basically what approaches looks like when you're doing a time series split. You are choosing date cutoffs. Nope, stop cutting me around. You're moving. You're choosing the date cutoffs here. For example, you're saying all the data that's before August 1st. You're evaluating it. And then you're choosing the time differential to say, I want it to be anything.

I want to figure out what the tests will look like. if they were greater than September 1st. So you're training the data set before August. You are evaluating the data set between August 1st to September 1st. And then you're trying to predict data sets for September 1st. This is where a lot of the systems we're doing is actually built properly on is how am I now training and testing this data? What am I doing to actually predict the actual modeling for what it would look like to go outwards?

contract if they ever fire the evaluation as fiction they have to run them at split times so they have to be run separately basically to be able to do it you first spend the time training you evaluate and then you continue to test does that make sense so far Yep, go. Yep. Okay. So, Um... This is again another approach and this is where we're talking about grouping and entity grouping. We're choosing basically to group things based on latitude and longitude. This is where we're going to spend a lot of our time choosing to kind of cluster our data sets.

This for example, this data this example chooses to cluster the entire data in five clusters. A lot of this basically is dependent on you You really, and I think this is where I'm really going to spend a lot of my time trying to evaluate is, are you spending the time to look at what you have and try to build a system that's coherent, that is clustered, that is predictable, and that continues to kind of prove the entire system state right over time, every single time. This is basically what matters the most.

It's going to be, how are you clustering this data? How are you spending the time to train models, to build models that actually are prepared for how you're doing?

This is like, I know we're talking about a lot of these systems, but it's really, really matters for what we're trying to actually build and do.

Okay, so The other thing I want to talk about is a lot of your systems And a lot of what you're trying to do is very dependent on multiple data sets. And I think that's basically what we talked about and spent most of our time doing this past week is how are we getting a lot of different data sets to support the systems we're building? What's important to talk about is each one of these entities live in exactly one set. So if you have air quality, if you have buildings, you have patients, if you have sensors, group them by station IDs, by building IDs, by patient IDs, by device ID, and then train the stations, for example, air quality, train the model on stations one to seven, test it on models eight to 10, and you're predicting should have an unseen stations.

to focus on out of time energy here is is that you have a large enough data set where you're able to train for all of the data you have and predict the majority of it so if you're great example here if you're training your data set from if you have 10 stations and you use one to seven to prepare and train on it you should be able to predict eight and ten this is a very small subset i'm hoping that we're using way way larger of the data sets for us to actually build on this and model on it Basically a really, really easy example of what we're talking about here.

Right. So the single hardest thing in discipline is basically the touched ones. It's that If you write a test set parquet at split time, you cannot supposed to be looking at it the model is locked in its hyper-grounders. It's something that's commonly missed in that if you actually try to test it, you're basically breaking it. This is kind of one of those systems that is very, very difficult to think about when your model is there.

It's something I continuously challenge myself with in XOAT, so I would understand if we're moving away from that. Okay. Let's talk about baselining. Okay, baselining. is the second aspect of the system when you are choosing to model what you're building, how does it look like to baseline and set a standard for what you're going to compare your data sets against. So, Okay. The baseline, basically, as you know, is basically the standard of where all of your data is measured against. Everything is going to be measured against it. And why does the baseline always come first? It's because it evaluates what does good mean as a standard for you to actually be looking at your data set to say, oh, this is good, or this is bad, or this is great. So if you are choosing to evaluate a model, and the model needs to have a baseline of 0.1, basically, that's very, very impressive.

And then I think that when we continue to evaluate for something that's too simple, predict it it's not really modeling as much as it is trying to build the systems Um... Okay. Some great examples of how we model and set baselines for what we're trying to build. If we have a dumb baseline, which is a mean mode basically, where we would be predicting regression. Or a train mean, or a classification, and it's the most frequent class, it's the floor. This is something where your model basically has captured any signal at all. It doesn't evaluate that you have a different kind of thing that you persisted, you're just choosing to persist anything.

And this is a very, very easy way to just say I'm predicting things at a baseline of mean or mode. which is I have a data set of hundreds of thousands of things and I choose the mean or mode and I say this is my baseline. This is a good baseline to say, depends on what you're doing, but it's a good baseline to set the standard of here's what I'm going to set everything against. Let's say I have, it's like evaluating what a Gaussian curve looks like. You have all of these numbers for student tests.

And then you get the mean and mode. And these are good indicators of what the baseline of how students performed, right? I think this is a very, very simple approach for what does baseline mean. You have another way, which is called persistence, which you can look like for time series. And then this is where you can look like you can capturing signals that are beyond inertia. It's basically what the hard set assessment is.

And you can say, I'm going to capture a time series of everyday student tests. That's a different approach. over time, then I can predict how they continue to perform afterwards. You have the next one, which is the spatial nearest as a baseline, where whenever you have spatial data, You can choose any point and then say this is where the mean is the nearest measured point of the system. And this is a really good indicator for us to capture the signals beyond any kind of geographies that are there.

And then the last way for us to measure baselines is through something called domain heuristics. I think this is where any kind of person uses it. It helps us, if that's an engineer or a planner or whoever it is. It's a system that sets the capturing signals beyond what the field already knows. And this is the most useful baseline. And this is basically what a lot of us are doing. You are choosing a very specific domain.

You're choosing a very specific problem to solve. The main heuristics are going to be on what does it look like to actually be assessing and tripping the systems. So I think the biggest problem that we have to see a lot of in the modeling systems is that you don't really have a model. You basically have a detector of what you're trying to do. And I think that that's something that we have to address a lot of at the times. And when we do get this and this happens to us, we have to evaluate, is our brief wrong? Is the system just not really carrying what we want to build?

Does the feature not carry any signals? Are the models too weak? We'll evaluate if what we're doing sets the baseline that we want to continue to build against. Um, This is something that I also want you guys all to take away from it is what does the problem shape? What's the data size and dimensionality and will you be asked to explain it? These evaluate what models and what baselines we're going to continuously build together to talk about how are we going to actually evaluate what it looks like and how it looks like.

This is very important for us to actually look at, which is when we're looking at What does it look like to adopt your data? I'm gonna say there are a few things in future approaches for us to do what it looks like. We have to start usually oftentimes boring, we can do regression, classifications, time series, spatials, points predictions, image sequencing. I actually wanted to talk to you guys. Have any of you, maybe whether through this master's or before in your undergrads, done any sort of prediction modeling through any kind of regression classification?

Have you worked with these systems before? Basically.

Yeah, I think in our first semester, we worked on a project where we used prediction modeling to predict crowd pattern behaviors. And it was mostly an image-based system at that point of time. But if we had used an agent-based system, then we probably could have used regression as well. But at that point of time, it was just, you prediction based.

Okay, and how was that class? Was it something that you felt like, oh my God, this is brand new information to me? Or did you adapt and walk away from it to being like, okay, I basically understand these four approaches. Basically what I'm trying to grasp at here is, do we want to dive in a little deeper in our workshops to talk about how to make these prediction modelings and understanding them deeper?

Or have you guys covered this before?

So I think it was just a group that kind of, I think there were two groups in the class that worked on prediction modeling that semester. And I think it was brand new information at that point of time. I mean, I let other people also answer, but I wouldn't mind knowing a little bit more because we kind of stumbled and figured it out by ourselves. Okay.

Okay, I see. So...

I also used the time series, the only one I ever saw before. They use it in flood prediction. Hmm. So I worked a little bit with that kind of just at the time it was in my undergrad like just an excel spreadsheet and we had this kind of time series graph where you could see one in a 50 year flood 100 year etc. Okay.

That's awesome. That's awesome. Yeah. Okay. Has anyone else used it? Yeah, tell me.

Yes, we've also worked in the first semester, our group on CMS-AUNAT model, which basically works with images and we were predicting from pre-image and post-image of disasters where the damaged buildings would be masked, basically.

Okay, so this is great. This is a great approach. I think, yeah, I'll talk to you guys all in your group separately, but I think that it's a great way for kind of building this system to understand how we can choose how to predict so that we're able to actually build systems that predict well and can be used by whoever your ICP is. So yeah, maybe what I'll do is I don't know if any of you booked a session with Salvador, but I would really, really encourage you to do that if you want to continuously build what you're making.

But what I'll do today is I'll try to spend some time with each of you guys separately to... look at how you're doing and how I can help. But yeah, this is awesome. Okay. Cool. Just that we have a few more slides and we can start getting into it. I think that the biggest thing is, Almost always a linear model just works, right? I think that deep learning, and I know sounds fancy and you want to talk about all these things, you need millions of examples, right?

And then things that are simple, like what we're talking about here before, which is regression or classifications or, sorry, regression or classifications or image sequencing or spatial predictions often give you very, very good realized data for what you want to talk about. And I think, Um, Yeah, you have 5000 rows, you have 12 features, your linear model is going to work. You don't need some deep learning AI. You want to say I build, you know, you're not making an LLM, right?

You're not making any kind of system that's going to work on it. And I think this is why we talk about boring usually wins is because this is what basically gives you the best kind of answers based on the data sets that you have. Um, This is also very, very important to talk about, which is how are you assessing the metrics that you're building? And I think that with that, it matters a lot what approach you chose to come with.

If you're choosing regression, then that's something that you're going to be using it for interpretable units, any kind of R squared. And this allows us to kind of build the baseline for how biased the answers are. do balanced classifications, which are accuracy metrics, and we can do imbalanced, which are precision metrics based on how we have. We can do forecasting, and I think this is something I use most of the time. We can also do uncertainty classifications.

I know a lot of them basically just has different, different metrics and valuation, but what I want to go back to at the beginning, which might seem very, very daunting, which is where is it? The separation of responsibility between you and the AI that exists with us today. I lost it. is very, very good. And I want us to go back to this every single time. What matters to most, especially in this new age of what we're trying to do, is you have defensible systems. If what you have, and I will continue to say this, is what you have, you understand, then that's all that matters.

So if you are the one that's making a decision that you want to use image sequencing because you've evaluated and spent all this time studying that this is what works best for you. And if you spend all this time now choosing to use a regression testing, because again, you understand how it works, then how this is implemented can be delegated to the LLM that you're working with. And that's basically what we're trying to get to.

And I know we kept talking about it. It's just, As long as you're able to defend what you've built, and as long as you're able to understand how you have, and it's not some AI slob that you one-shotted, you don't need to get into the really, really niche systems of how did this AI make an R-squared variance system. As much as it is that I understand the AI did this, this is how it works, this is how the systems are built, and the execution can be determined to be delegated.

And I think that's what I continue to see in the industry, which is systems are delegated The systems are designed by humans and execution is delegated to LLMs. Okay, so what, sorry, that was a very unnecessary tangent, but I think it's important to address.

No, I think super, super cool. Um...

Yeah, like I, We have a Toronto Tech Week right now in Toronto and everyone's just talking crazy things about AIs and systems. Yeah, I mean, we're moving towards a day where you're no longer ever going to have to write codes and that's fine. But no one understands what they're writing and that's the problem. And I think that's where we want to move against.

Yeah, if a software developer would kind of develop the software in like two, three weeks instead of two days, but whenever a bug would come, the guy would know where to kind of...

Exactly.

Exactly. Spend two weeks asking.

And I think that like this now comes back upwards when you're designing systems for people to make decisions against. You're designing systems that you're supposed to predict and model. I don't, no one expects you to understand how this code is written. I expect you to understand how the system is designed. I expect you to understand what it looks like and how it's doing it and what approaches of systems are being made because you're the architect.

And I think now, It's crazy. Sorry, let's just go the tangents for just five minutes. It's crazy because now every single person in this new age is now an architect. Right. Everyone is now just designing systems and no longer a developer or no longer whatever, a writer. It's just you are designing and thinking about what it needs to look like. And now that's become the most valuable trait to have, which all of you have an insane advantage of because you're all approaching this from the methodology and how you think.

And I think what this entire seminar is based off of is how do you apply this way of thinking into these systems? Because what you have been taught, How you've been having with degrees in architecture is this is basically the most valuable things you have. The methodology of thinking. Yeah. It's pretty cool. Okay, so we're always reporting the matrix. We're never basically reporting the headline. I think this is just basically, like you can see basically what I'm doing is just basically putting examples up.

If you have one number, it's not a model card. I think this one matters the most. These are things you talk about for what it looks like. I have my training, my evaluation and my testing. This matters a lot. If you chose a baseline metric to measure, I've trained it against this metric. I chose a dumb mean. And I persisted it for this much and I had an RF model. When I evaluate it, I should get something that's close, and when I test it, I should get something that's close. This basically tells me how did I perform.

And I think that's what a lot of the things I'm submitting for you guys to look at has, is a lot of these systems.

So if any of these accesses are not present, your table is not accurate at all. You need to have the splits, the models, threads, and the segments that you chose to split it in. So you're choosing to assess it based on valuations or testing. You're choosing how you're testing the system. You're choosing what the fold and how the standard deviation breaks out. And you're choosing the performance that is by session, whether that's going to be any, session but basically how are you driving into the season and station as the classes Um...

So another thing to talk about is that the point prediction is not really talking about the confidence of the intervals. I think this is something that gets way too technical that we can talk about. We can completely not talk about this if it's not necessary. It just basically addresses the different variations.

Um...

The things I want to basically have the most in your modeling cards, which is what's the baseline that you're choosing to beat? How is the spreading and what new systems are you choosing to design out of it? These are systems that you want to talk about. And I think the one thing we want to do is we're going to do some notebooks and we're going to make some artifacts and how we're going to be building it.

Here's an example of code that we're going to talk about, which is I'm basically putting these for me to kind of keep track of what you're doing, but it's an artifact. It's supposed to have weights. It's supposed to have transforming models, it's supposed to have some prediction chains. These are things we need to be looking at as well a lot and it continues to be the standard for what it loads from the disk.

for us to predict the models of what we're trying to answer. And I think that the thing that's basically different with what we're expecting in the seminar is that Because we spent a lot of this time having the data and making the data and choosing the data, and now we're going to spend the next sessions of our time modeling this data and building AI systems, I do not want any of you to be deviating away from what the final solution looks like for the user, which does have some sort of system that's user-interfaced that does allow us to kind of predict and showcase how the users can make decisions and have this be the foundations for them.

Yes, we're modeling this, but And I'm going to see you guys again after tomorrow. We're running, we're like shorting out the times we have and I'm actually so excited that we have two sessions this week because it allows us to actually stay engaged and not rebuild momentum every single week. Be passionate about what you're building for who at the end. Because if you have that, then you're able to understand how you're going to be training these models.

Keep this brief that you looked at in the beginning and the first session that you made in mind when we're talking about what we're needing to build now and what we're going to be building for who, because it allows us to focus our energy and time into how to model these systems and on what metrics to choose. Those are basically the biggest things I want to talk about. Now, what are we submitting? We're going to be submitting some more MD files, which again, I expect your AI systems to help you a lot with writing and that's fine. But I think that this is a data sheet on how you're going to be modeling the answers.

What are the answers? How are you predicting these numbers and systems? I think the other thing is that You should be listing at least three things that your model is not for. You can say this is not for regulatory air quality compliance. You can say not for individual level health advice, not for prediction outside the train's spatial extent. Set the actual boundaries for where and how it's supposed to be used because that allows us to actually separate what and how to use it. Um...

This is another file and then here is where I think I'll give you guys an example. AI can Without AI, doing this task would take you weeks. I remember when I was... Helping a couple of classes, I think two years ago with this entire exact same thing with IAC. They took basically the entire seminar. The entire seminar was just on trying to model a system. And now we're trying to model it in the next three, four days.

This basically shows you how much to what we were talking about earlier Rafiq, how much AI can actually assist in your systems We're going to model this entire, we're going to train this model and build it out in the next two, three days because you can. and it's not hard to do so because you can just understand what you want to do and it can help you to do it. We're going to specify the problem. Please be direct, verify it, iterate it, card it.

I'm going to send this a screenshot. because I don't want anyone to Actually, I'll just upload the entire PDF. Please take spend a lot of this time trying to understand how to plan this out Where we're at And how does this deviate from what we talked about? This is the part where I hope to you guys is exciting. We got the data last time, we're going to be modeling it today. We spent all this time trying to get the data and clean it up Today or for the next session, we're going to split the phase, train the phase and plan what it looks like for us to get this out.

And I think this here, if I look at a screenshot for just for you guys to get the vision of what we're doing, Us getting the model ready is all what matters because in the next two to three sessions, we're going to be synthesizing data, we're going to be stress testing the data, and we're going to make some UXs and UIs for us to actually use this model. And not just say, I have a model that works. Because a useful model is something that allows us to actually work on how we want to do these systems.

Yeah, we're not generating fake data. We're not going to make galleries. We're not gonna make any UIs. We're not going to tune any secondary models. Please only tune one. And we're going to basically focus energy on trying to parameter sweep. Your baseline is defensible and it has to be worth it. I continue to use the same themes, but it's important to talk about that you have to be defensible. And where we're going to be talking about is, yep, that's okay. I'm going to try to test some of your models.

I'd love to pull them out and test, pull it and test if it works and what we're trying to do. And I'm going to walk around and go to each of your rooms to kind of address where we're at and how the systems are there. So we're going to try to get there as well. I will upload the models, upload the new files into the systems and I'll upload the things to upload to use in your GitHub repos. And I think that's what we're going to be talking about for an expectation.

and Let's go. Any questions before I make it to groups? I'm going to spend like maybe five. I'll give you guys five minutes. You guys can go into your breakout rooms and then I'll come. I'll join you guys. But any questions? Is there anything you guys want to talk about before we get into this? Does it make sense? I know this is where it usually gets very daunting for everyone. So please feel free to ask anything.

I'll give you guys maybe the next one or two minutes if you have any questions.

I think we'll take some time to go through it before we-OK.

So I'll open up the rooms. And then you guys can go into them and I'll join you guys and we'll talk about it one more time. And we have four rooms. It's... Hello. Okay, amazing.

No, this is not... Oh shit! It's not my group. Hello? Hi, yes, he invited me to this one, but I'm going to leave it. I just clicked, yeah, so it's not my fault. Hmph.

Oh, sorry.

Give me a second. I'll just... Where did he throw us now?

Yeah, same. John, break out room one. Where did he throw us?

It shows to break them out to you guys however way you want, which is... Breakout rooms. Hostels. um I have to wait 35, okay, one second. Recreate. Assign menu then, right-click, supposed to choose reference. Okay. There you go. It's a sign that's manually to you guys. Everyone picks their own rooms for some reason.