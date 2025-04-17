import plotly.graph_objects as go
from data_collector  import DataCollector
from pptx_utilities import *

class SlidesCollector(DataCollector):
    def create_slides(self, name : str, template_path : str):
        """Метод создаёт слайды из шаблона .pptx презентации
            Args:
                name (str): имя руководителя
                template_path (str): путь к .pptx шаблону
        """
        raw_name = name
        name = self.contains(name)
        if name is None:
            print(f"Name \"{raw_name}\" not found")
            return
        
        filled_groups = self.__select_filled_groups(name)
        if len(filled_groups) == 0:
            print(f"For name \"{name}\" not enough data")
        elif len(filled_groups) == 1:
            self.__create_slides_one_level(name, filled_groups[0])
        elif len(filled_groups) == 2:
            self.__create_slides_two_levels(name, tuple(filled_groups))
        elif len(filled_groups) == 3:
            self.__create_slides_three_levels(name)

    def __select_filled_groups(self, name : str) -> frozenset[int]:
        structure  = self.survey_structure 
        valid_groups = list()
        index = 1
        for group_name, columns in structure["groups"].items():
            groups = structure.create_group_structure(columns)
            counter  = 0 
            report = self.get_person_report(name, group_name)
            for question_nmb in groups["select"]:
                if question_nmb in structure["output headers"] and report[structure["output headers"][question_nmb] + "_count"] > 0:
                    counter += 1
                    continue
                if question_nmb not in structure["output headers"] and report[structure["questions"][question_nmb][1] + "_count"] > 0:
                    counter += 1
            if counter == len(groups["select"]):
                valid_groups.append(index)
            index += 1
        return valid_groups

    def __create_slides_one_level(self, name: str, level: int):   
        level_name = levels[level]
        level_table = levels_table[level]
        pres = Presentation("resources\\template.pptx")
        default_msg = "Недостаточно данных"
        select_slides(pres, [5])
        report = self.get_person_report(name, level_name)

        #set positive/negative sides
        update_cards(pres.slides[0], report, levels[level])

        #set name
        update_text(pres.slides[0].shapes[1].text_frame, name)

        #set feedback
        feedback = "Обратная связь:\n" + (default_msg if report[f"Обратная связь, {level_name.lower()}_count"] < 2 else 
            report[f"Обратная связь, {level_name.lower()}_feedback"])
        update_text(pres.slides[0].shapes[3].text_frame, feedback)

        #set ratings
        update_table_cell(pres.slides[0].shapes[2].table, 0, 1, level_table)
        ratings = self.get_person_ratings(name)
        rating = default_msg if ratings[level - 1][1] < 2 else f"{ratings[level - 1][0]:.1f}"
        update_table_cell(pres.slides[0].shapes[2].table, 1, 1, rating)
        overall_rating = self.get_average_rating([4,11,20])["Overall"]
        update_table_cell(pres.slides[0].shapes[2].table, 1, 2, f"{overall_rating:.2f}")
        
        pres.save(f"outputs\\{name}.pptx")

    def __create_slides_two_levels(self, name: str, level: tuple[int,int]):
        pres = Presentation("resources\\template.pptx")
        default_msg = "Недостаточно данных"
        select_slides(pres, [3,4])
        report = self.get_person_report(name)

        #update charts
        update_chart(pres.slides[0].shapes[3].chart, self.get_select_vals_for_plot(name, levels[level[0]]))
        update_text(pres.slides[0].shapes[3].chart.chart_title.text_frame, levels_chart[level[0]])
        update_chart(pres.slides[1].shapes[3].chart, self.get_select_vals_for_plot(name, levels[level[1]]))
        update_text(pres.slides[1].shapes[3].chart.chart_title.text_frame, levels_chart[level[1]])

        #set name
        update_text(pres.slides[0].shapes[1].text_frame, name)
        update_text(pres.slides[1].shapes[1].text_frame, name)

        #set feedback
        feedback = "Обратная связь:\n" + (default_msg if report[f"Обратная связь, {levels[level[0]].lower()}_count"] < 2 else
            report[f"Обратная связь, {levels[level[0]].lower()}_feedback"])
        update_text(pres.slides[0].shapes[4].text_frame, feedback)

        feedback = "Обратная связь:\n" + (default_msg if report[f"Обратная связь, {levels[level[1]].lower()}_count"] < 2 else 
            report[f"Обратная связь, {levels[level[1]].lower()}_feedback"])
        update_text(pres.slides[1].shapes[4].text_frame, feedback)

        #set ratings
        ratings = self.get_person_ratings(name)

        def update_table(slide):
            update_table_cell(slide.shapes[2].table, 0, 1, levels_table[level[0]])
            rating = default_msg if ratings[level[0] - 1][1] < 2 else f"{ratings[level[0] - 1][0]:.1f}"
            update_table_cell(slide.shapes[2].table, 1, 1, rating)

            update_table_cell(slide.shapes[2].table, 0, 2, levels_table[level[1]])
            rating = default_msg if ratings[level[1] - 1][1] < 2 else f"{ratings[level[1] - 1][0]:.1f}"
            update_table_cell(slide.shapes[2].table, 1, 2, rating)

            overall_rating = self.get_average_rating([4,11,20])["Overall"]
            update_table_cell(slide.shapes[2].table, 1, 3, f"{overall_rating:.2f}")
        
        update_table(pres.slides[0])
        update_table(pres.slides[1])
        
        pres.save(f"outputs\\{name}.pptx")

    def __create_slides_three_levels(self, name: str):
        pres = Presentation("resources\\template.pptx")
        default_msg = "Недостаточно данных"
        select_slides(pres, [1,2])
        report = self.get_person_report(name)

        #update charts
        update_chart(pres.slides[0].shapes[3].chart, self.get_select_vals_for_plot(name, "Непосредственный руководитель"))
        update_chart(pres.slides[1].shapes[1].chart, self.get_select_vals_for_plot(name, "Вышестоящий руководитель"))
        update_chart(pres.slides[1].shapes[2].chart, self.get_select_vals_for_plot(name, "Функциональный руководитель"))

        #set name
        update_text(pres.slides[0].shapes[1].text_frame, name)
        update_text(pres.slides[1].shapes[5].text_frame, name)

        #set feedback
        feedback = "Обратная связь:\n" + (default_msg if report["Обратная связь, непосредственный руководитель_count"] < 2 else 
            report["Обратная связь, непосредственный руководитель_feedback"])
        update_text(pres.slides[0].shapes[4].text_frame, feedback)

        feedback = "Обратная связь:\n" + (default_msg if report["Обратная связь, вышестоящий руководитель_count"] < 2 else
            report["Обратная связь, вышестоящий руководитель_feedback"])
        update_text(pres.slides[1].shapes[3].text_frame, feedback)

        feedback = "Обратная связь:\n" + (default_msg if report["Обратная связь, функциональный руководитель_count"] < 2 else
            report["Обратная связь, функциональный руководитель_feedback"])
        update_text(pres.slides[1].shapes[4].text_frame, feedback)

        #set ratings
        ratings = self.get_person_ratings(name)
        rating = default_msg if ratings[0][1] < 2 else f"{ratings[0][0]:.1f}"
        update_table_cell(pres.slides[0].shapes[2].table, 1, 1, rating)

        rating = default_msg if ratings[1][1] < 2 else f"{ratings[1][0]:.1f}"
        update_table_cell(pres.slides[0].shapes[2].table, 1, 2, rating)

        rating = default_msg if ratings[2][1] < 2 else f"{ratings[2][0]:.1f}"
        update_table_cell(pres.slides[0].shapes[2].table, 1, 3, rating)

        overall_rating = self.get_average_rating([4,11,20])["Overall"]
        update_table_cell(pres.slides[0].shapes[2].table, 1, 4, f"{overall_rating:.2f}")
        
        pres.save(f"outputs\\{name}.pptx")

    def create_plot(self, name : str, group : str):
        person_stat = self.get_select_vals_for_plot(name, group)
        colors = ['rgba(168,209,141,0.8)',
                'rgba(251,114,134,0.8)']

        x_data = person_stat[1]
        y_data = person_stat[0]
        fig = go.Figure()

        for i in range(0, len(x_data[0])):
            for xd, yd in zip(x_data, y_data):
                fig.add_trace(go.Bar(
                    x=[xd[i]], y=[yd],
                    orientation='h',
                    marker=dict(
                        color=colors[i],
                        line=dict(width=0)
                    )
                ))

        fig.update_layout(
            xaxis=dict(
                showgrid=True,
                showline=False,
                tickformat= '0.00%',
                showticklabels=True,
                color="white",
                zeroline=True,
                domain=[0.15, 1]
            ),
            yaxis=dict(
                showgrid=False,
                showline=False,
                showticklabels=False,
                zeroline=False,
            ),
            barmode='stack',
            paper_bgcolor='rgb(0, 0, 0)',
            plot_bgcolor='rgb(0, 0, 0)',
            margin=dict(l=300, r=10, t=140, b=80),
            showlegend=False,
        )

        annotations = []

        for yd, xd in zip(y_data, x_data):
            # labeling the y-axis
            annotations.append(dict(xref='paper', yref='y',
                                    x=0.14, y=yd,
                                    xanchor='right',
                                    text=str(yd),
                                    font=dict(family='Arial', size=14,
                                            color='rgb(255, 255, 255)'),
                                    showarrow=False, align='right'))
            # labeling the first percentage of each bar (x_axis)
            if xd[0]!=0:
                annotations.append(dict(xref='x', yref='y',
                                        x=xd[0] / 2, y=yd,
                                        text=str(int(xd[0]*100)) + '%',
                                        font=dict(family='Arial', size=14,
                                                color='rgb(0, 0, 0)'),
                                        showarrow=False))
            # labeling the second percentage of each bar (x_axis)
            if xd[1]!=0:
                annotations.append(dict(xref='x', yref='y',
                                        x=xd[0] + (xd[1]/2), y=yd,
                                        text=str(int(xd[1]*100)) + '%',
                                        font=dict(family='Arial', size=14,
                                                    color='rgb(0, 0, 0)'),
                                        showarrow=False))

        fig.update_layout(annotations=annotations, title=dict(text=group, x=0.5 ,font=dict(size=50, color='rgb(255, 255, 255)')))
        fig.update_traces(width=0.5)
        fig.show() 