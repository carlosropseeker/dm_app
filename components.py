import streamlit as st

def slider_component(f1, f2):
    container = st.container()
    if f1+"@"+f2 not in st.session_state.sliders.keys():
        st.session_state.sliders[f1+"@"+f2] = 0
    option = container.selectbox('¿Qué factor es más importante para ti, {} o {}?'.format(f1, f2),[f1,f2])
    slider = container.slider('¿Cuánto más importante?', 0,9, key=f1+"@"+f2, value=st.session_state.sliders[f1+"@"+f2])
    st.session_state.sliders[f1+"@"+f2] = slider
    return {'choiceOne':option, 'choiceTwo': f1 if f1!=option else f2, 'value':slider}

def alternative_evaluation_component(name, description, factors):
    container = st.container()
 
    container.write('The alternative {} is characterized by {}. Please rate {} with respect to each of the following factors:'.format(name, description, name))
    toret = {'alternative': name, 'values':[]}
    for factor in factors:
        if name+'@'+factor not in st.session_state.alternatives.keys():
            st.session_state.alternatives[name+'@'+factor] = 0
        slider = container.slider(factor, 0,9, key=name+'@'+factor, value=st.session_state.alternatives[name+'@'+factor])
        st.session_state.alternatives[name+'@'+factor] = slider
        toret['values'].append((factor, slider))
    return toret