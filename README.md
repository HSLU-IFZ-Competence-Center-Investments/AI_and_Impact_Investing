# AI and Impact Investing

![Cover.jpg](https://github.com/HSLU-IFZ-Competence-Center-Investments/AI_and_Impact_Investing/blob/main/DATA/Images/Cover.jpg)

### Initial situation

With the rapid development of artificial intelligence systems, especially large language models (LLMs) and their ability to process natural language, various applications of this technology seem possible in almost any field. The financial sector, which has large amounts of information at its disposal, could benefit from this development by further simplifying the extraction and analysis of relevant data to streamline operations, enhance decision-making, and improve customer experiences. This also applies to sustainable investing, an area that is becoming increasingly important as investors seek greater transparency and accountability in sustainability practices of companies they invest in.

The present repository provides a prototype to create a company ranking of the 17 SDGs for each of the companies underlying two exemplary Swiss investment funds. For this purpose, company-specific information is extracted from public websites and subsequently analysed using LLMs from OpenAI to assess its relevance to each of the SDGs. Please note that the used company names and extracted text files have been replaced by dummy names and files in order to anonymise the inspected investment funds in agreement with the fund provider.

It is evident that the developed prototype does not address the underlying issues of lack of progress on the SDG targets. However, it could facilitate the review of SDG alignment for specific companies and investment funds, potentially validating corresponding SDG assessments and providing transparency for investors.

### Prototype description

The prototype's design and task flow are illustrated in the figure below, displaying its four main components to generate SDG rankings. Firstly, the underlying companies of two private equity funds were identified and the domains of their public websites, which provide the data source for creating the desired ranking, were collected. Secondly, a web scraping module gathered the public information of the websites as HTML files and extracted the text components. After applying data-preparation measures to the saved text files, the company information was fed to a GPT assistant (OpenAI Assistant API v1) in the third step. For example, the individual text files of each company were combined into one larger text file, including the page names as headers, to comply with the maximum of 20 files for each session of the assistant. The AI assistant, acting as an SDG expert, was asked to review the text files of each company, indicating which information is deemed relevant and to finally return a SDG ranking for each entity. For this step, multiple prompting approaches were tested to obtain the desired ranking on the basis of the available, non-SDG-specific information. 

![Prototype_Architecture.JPG](https://github.com/HSLU-IFZ-Competence-Center-Investments/AI_and_Impact_Investing/blob/main/DATA/Images/Prototype_Architecture.jpg)

### Testing the prototype 

The demo can be accessed locally by [forking the repository](https://docs.github.com/en/get-started/quickstart/fork-a-repo), installing the packages indicated in requirements.txt and running the file run.py. If you have not worked with GitHub before, [set up Git](https://docs.github.com/en/get-started/quickstart/set-up-git) first.

- In an existing environment you can install packages using the following terminal command: pip install -r requirements.txt
- Please consult this guide if you are unsure how to set up a [new environment](https://realpython.com/python-virtual-environments-a-primer/#create-it).

When starting run.py, you will be asked to enter an [OpenAI API key](https://platform.openai.com/account/api-keys), since the prototype runs with the paid LLM ChatGPT-4-turbo. However, the used model can also be changed in the chat.py file.

Furthermore; COMPANIES

### Known issues of the prototype

### Related report
The report was published on the [HSLU Retailbanking Blog](link) and is available publicly. 
