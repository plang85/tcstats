import sys, logging
import common
import datetime
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
matplotlib.style.use('ggplot')

#logging.basicConfig(level=logging.DEBUG)
#logging.basicConfig(level=logging.INFO)

min_date = datetime.datetime.now() - datetime.timedelta(days=2)

frames = []
rdata = common.get_tc('/projects/id:IntersectMain_RollingBuilds_Builds')
for build_type in rdata['buildTypes']['buildType']:
    build_data = common.get_tc(build_type['href'])
    build_name = build_type['name']
    ibuild_name_begin = build_name.rfind('Rolling')+7
    bname = build_name[ibuild_name_begin:]
    bname = bname.replace('Run ', '')
    tmp_start = []
    tmp_duration_hrs = []
    def for_each_build_page(page_data):
        for build in page_data['build']:
            data = common.get_tc(build['href'])
            start = datetime.datetime.strptime(data['startDate'], common.TC_TIME_FORMAT)
            if start < min_date:
                return False
            end = datetime.datetime.strptime(data['finishDate'], common.TC_TIME_FORMAT)
            duration_seconds = int((end-start).total_seconds())
            print('  {0}: {1}-{2} >> {3:d}s'.format(data['number'], str(start), str(end), duration_seconds))
            tmp_start.append(start)
            duration_hrs = duration_seconds/60**2
            tmp_duration_hrs.append(duration_hrs)
        return True

    common.traverse_linked_pages_tc(build_data['builds']['href'], for_each_build_page)
    
    date = pd.to_datetime(pd.Series(tmp_start))
    series = pd.Series(tmp_duration_hrs, index=date)
    frame = pd.DataFrame({bname:series.groupby(series.index.hour).sum()})
    index = [i for i in range(24)]
    frame = frame.reindex(index, fill_value=0)
    frames.append(frame)

frame = pd.concat(frames, axis=1)
frame.to_csv('data_tmp/buildeffort7.csv')
ax = frame.plot.bar(stacked='bar')
ax.set_ylabel('Duration (h)')
ax.set_xlabel('Time')
plt.savefig('data_tmp/buildeffort.png', dpi=600)
plt.show()