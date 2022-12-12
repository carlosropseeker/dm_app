import streamlit as st
import json
import ahp
import components as comp
import matplotlib.pyplot as plt
import boto3

def get_combinations(seq):
    combinations = list()
    for i in range(0,len(seq)):
        for j in range(i+1,len(seq)):
            combinations.append([seq[i],seq[j]])
    return combinations

def store_json_to_s3(data, bucket, key):
    s3 = boto3.resource('s3')
    s3object = s3.Object(bucket, key)
    s3object.put(
        Body=(bytes(json.dumps(data).encode('UTF-8')))
    )

if __name__ == '__main__':

    with open("./conf/conf.json") as file:
        f = json.load(file)
        alternatives = f['alternatives']
        factors = f['factors']
        combinations = get_combinations(factors)

    app_mode = st.sidebar.selectbox('Select Page',['Presentation', 'Factors', 'Alternatives', 'Send opinion', 'Discussion'])
    if not hasattr(st.session_state, 'sliders'):
        st.session_state.sliders = {}
    if not hasattr(st.session_state, 'alternatives'):
        st.session_state.alternatives = {}
    if not hasattr(st.session_state, 'results'):
        st.session_state.results = {}
    if not hasattr(st.session_state, 'priorities'):
        st.session_state.priorities = [1]*len(factors)
    
    if app_mode == 'Presentation':
        pass


    elif app_mode=='Factors':        
        st.title('Valoración de factores de decisión')  
        col1, col2 = st.columns(2)
        with col1:
            responses = [comp.slider_component(factorpair[0], factorpair[1]) for factorpair in combinations]
            matrix = ahp.gen_matrix(factors, responses)
            st.session_state.priorities = ahp.get_priorities(matrix)
            factor_rank = {f:p for f,p in zip(factors, st.session_state.priorities)} 

        with col2:
            if len(matrix) > 2:
                cr = ahp.calculate_consistency_ratio(
                    ci=ahp.calculate_consistency_index(matrix, st.session_state.priorities),
                    cr=ahp.calculate_random_consistency_index(len(matrix))
                )
            else:
                cr=1
            st.write('Tu consistencia respondiendo es de:')
            if cr <= 0.1:
                st.success(str(cr))
            elif (cr > 0.1) & (cr <= 0.3):
                st.warning(str(cr))
            else:
                st.error(str(cr))

            fig1, ax1 = plt.subplots()
            ax1.pie(st.session_state.priorities, explode=ahp.get_explode(st.session_state.priorities), labels=factors, autopct='%1.1f%%',
                    shadow=True, startangle=90)
            ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
            st.pyplot(fig1)


    elif app_mode == 'Alternatives':
        st.title('Alternatives evaluation')
        st.write('In this screen we ask you to evaluate each of the alternatives with respect to the decision factors')

        resp = [comp.alternative_evaluation_component(name, description ,factors) for name, description in alternatives.items()]
        prior = ahp.add_prior_by_attribute(factors, resp)
        res = ahp.add_endpoint_prior_by_action(prior, factors, st.session_state.priorities)
        st.session_state.results = ahp.add_weights(res)

    elif app_mode == 'Send opinion':
        st.title('Results verification')
        
        fig1, ax1 = plt.subplots()
        ax1.pie(st.session_state.results['weights'].values(), labels=st.session_state.results['weights'].keys(), autopct='%1.1f%%',
                shadow=True, startangle=90)
        ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        st.pyplot(fig1)

        st.write('If you agree with the results presented, you can fill in the last fields and send your results:')
        st.session_state.results["name"] = st.text_input('Name')
        st.session_state.results["email"] = st.text_input('Email adress')

        if st.button('save'):
            store_json_to_s3(st.session_state.results, f["bucket"], st.session_state.results["name"] + "@" + st.session_state.results["email"])


    elif app_mode == 'Discussion':
        pass